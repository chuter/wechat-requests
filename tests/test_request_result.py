# -*- encoding: utf-8

import pytest
import six

from wechat import result
from wechat.compat import json


class TestRequestResult:

    @pytest.mark.parametrize("ret_json", [
        {},
        {"openid": "openid", "age": 33, "time": "2018-04-28 18:41:00"},
        {
            "users": [{"openid": "openid", "age": 33}],
            "time": "2018-04-28 18:41:00"
        },
    ])
    def test_from_json(self, ret_json):
        request_result = result.build_from(ret_json)
        assert not request_result.is_failed
        for key, val in six.iteritems(ret_json):
            assert val == getattr(request_result, key)

    @pytest.mark.parametrize("ret_json_str", [
        '{}',
        '{"openid": "openid", "age": 33, "time": "2018-04-28 18:41:00"}',
        '''{
            "users": [{"openid": "openid", "age": 33}],
            "time": "2018-04-28 18:41:00"
        }''',
    ])
    def test_from_json_str(self, ret_json_str):
        request_result = result.build_from(ret_json_str)
        assert not request_result.is_failed
        ret_json = json.loads(ret_json_str)
        for key, val in six.iteritems(ret_json):
            assert val == getattr(request_result, key)
        assert ret_json_str.strip() == request_result.text

    @pytest.mark.parametrize("ret_xml", [
        '<xml><code>12</code></xml>',
        '''
        <xml>
            <code>12</code>
        </xml>
        ''',
    ])
    def test_from_xml(self, ret_xml):
        request_result = result.build_from(ret_xml)
        assert not request_result.is_failed
        assert request_result[u'code'] == u'12'
        assert ret_xml.strip() == request_result.text

    @pytest.mark.parametrize("ret_text", [
        'plaint text',
        '''
        <html>
            <body>htmlbody</body>
        </html>
        ''',
    ])
    def test_from_other_format_text(self, ret_text):
        request_result = result.build_from(ret_text)
        assert not request_result.is_failed
        assert ret_text.strip() == request_result.text
        assert {} == request_result.json

    @pytest.mark.parametrize("ret_text", [
        '{plaint text}',
        r'''
        {"d":,}
        ''',
    ])
    def test_from_invalid_json_str(self, ret_text):
        request_result = result.build_from(ret_text)
        assert not request_result.is_failed
        assert ret_text.strip() == request_result.text
        assert {} == request_result.json


class TestRequestErrorResult:

    @pytest.mark.parametrize("err_json", [
        {"errcode": 40013, "errmsg": "invalid appid"},
        {"errcode": 40002, "errmsg": "grant_type should be client_credential"},
    ])
    def test_from_json(self, err_json):
        request_result = result.build_from(err_json)

        assert request_result.is_failed
        assert request_result.errcode == err_json.get('errcode')
        assert request_result.errmsg == err_json.get('errmsg')

    @pytest.mark.parametrize("err_json_str", [
        '{"errcode": 40013, "errmsg": "invalid appid"}',
        '''
        {
            "errcode": 40002,
            "errmsg": "grant_type should be client_credential"
        }
        ''',
    ])
    def test_from_json_str(self, err_json_str):
        request_result = result.build_from(err_json_str)

        err_json = json.loads(err_json_str)
        assert request_result.is_failed
        assert request_result.errcode == err_json.get('errcode')
        assert request_result.errmsg == err_json.get('errmsg')

    @pytest.mark.parametrize("xml_str", [
        u'''
        <xml>
          <return_code>FAIL</return_code>
          <return_msg>签名失败</return_msg>
        </xml>
        ''',

        u'''
        <xml>
          <return_code>SUCCESS</return_code>
          <result_code>FAIL</result_code>
          <err_code>SYSTEMERROR</err_code>
          <err_code_des>签名失败</err_code_des>
        </xml>
        '''
    ])
    def test_from_xml(self, xml_str):
        request_result = result.build_from(xml_str)

        assert request_result.is_failed
        assert request_result.errcode in (u'FAIL', u'SYSTEMERROR')
        assert request_result.errmsg == u'签名失败'


@pytest.fixture(scope='class')
def response_builder(request):
    class FakeResponse(object):
        fake_status_code = 200
        fake_text = u''

        def __init__(self, status_code=None, text=None):
            self.status_code = status_code or self.fake_status_code
            self._text = text or self.fake_text

        @property
        def request(self):
            return None

        @property
        def text(self):
            return self._text

        def json(self, **kwargs):
            try:
                json.loads(self.tex)
            except Exception as error:
                raise ValueError(error)

    def builder(cls, status_code=None, text=None):
        return FakeResponse(status_code, text)

    request.cls.response = builder


@pytest.mark.usefixtures("response_builder")
class TestResultParseFromResponse:

    @pytest.mark.parametrize("ret_json", [
        {"openid": "openid"}
    ])
    def test_from_json(self, ret_json):
        response = self.response(text=json.dumps(ret_json))

        request_result = result.build_from_response(response)
        assert not request_result.is_failed
        assert request_result.json == ret_json

    @pytest.mark.parametrize("xml", [
        ' <xml> </xml>',
        ' <xml></xml> ',
    ])
    def test_from_xml(self, xml):
        response = self.response(text=xml)

        request_result = result.build_from_response(response)
        assert not request_result.is_failed
        assert request_result.text == xml

    @pytest.mark.parametrize("ret_text", [
        '{',
        '{"openid":}',
    ])
    def test_from_err_json_parse(self, ret_text):
        response = self.response(text=ret_text)

        request_result = result.build_from_response(response)
        assert not request_result.is_failed
        assert request_result.text == ret_text

    @pytest.mark.parametrize("err_json_str", [
        '{"errcode": 4001, "errmsg": "4001 error"}',
        '{"errcode": 4002}',
    ])
    def test_from_err_json(self, err_json_str):
        response = self.response(text=err_json_str)

        err_json = json.loads(err_json_str)
        request_result = result.build_from_response(response)

        assert request_result.is_failed
        assert request_result.errcode == err_json['errcode']
        assert request_result.errmsg == err_json.get('errmsg', '')

    @pytest.mark.parametrize("xml_str", [
        u'''
        <xml>
          <return_code>FAIL</return_code>
          <return_msg>签名失败</return_msg>
        </xml>
        ''',

        u'''
        <xml>
          <return_code>SUCCESS</return_code>
          <result_code>FAIL</result_code>
          <err_code>SYSTEMERROR</err_code>
          <err_code_des>签名失败</err_code_des>
        </xml>
        '''
    ])
    def test_from_err_xml(self, xml_str):
        response = self.response(text=xml_str)
        request_result = result.build_from_response(response)

        assert request_result.is_failed
        assert request_result.errcode in ('FAIL', 'SYSTEMERROR')
        assert request_result.errmsg == u'签名失败'

    @pytest.mark.parametrize("status_code", [300, 400, 500])
    def test_status_error(self, status_code):
        response = self.response(status_code=status_code)
        request_result = result.build_from_response(response)

        assert request_result.is_failed
        assert request_result.errcode == status_code
