# -*- encoding: utf-8

import time
import pytest
import mock

from wechat import mpapi, RequestException
from wechat import settings

from .compat import parse_qsl, urlparse


@pytest.fixture(scope="class")
def base_mpapi(request, mp_access_token):
    mpapi_instance = mpapi.formp(mp_access_token)
    request.cls.mpapi = mpapi_instance


@pytest.mark.usefixtures("base_mpapi")
class TestBaseMpApi:
    mp_access_token_qskey = 'access_token'

    @pytest.mark.parametrize("method", ['get', 'post'])
    def test_auth(self, mp_access_token, httpbin, method):
        """params会增加access_token信息
        """
        request_func = getattr(self.mpapi, method)
        mpresp = request_func(httpbin(method.lower()))
        actual_params_dict = dict(parse_qsl(
            urlparse(mpresp.request.url).query
        ))
        assert actual_params_dict[
            self.mp_access_token_qskey
        ] == mp_access_token

    def test_get_params(self, httpbin):
        mpresp = self.mpapi.get(httpbin('get'), openid="openid", name="chuter")
        actual_params_dict = dict(parse_qsl(
            urlparse(mpresp.request.url).query
        ))

        assert actual_params_dict['openid'] == 'openid'
        assert actual_params_dict['name'] == 'chuter'

    @pytest.mark.parametrize("method, request_params", [
        ('GET', {"timeout": 2, "headers": {}, "allow_redirects": True}),
        ('POST', {"timeout": 1, "headers": {"User-Agent": "dummy-agent"}}),
        ('PUT', {"timeout": 2, "headers": {"hk": "hval"}}),
        ('DELETE', {"cookies": {"ckey": "cval"}})
    ])
    def test_request_params(self, httpbin, mocker, method, request_params):
        """测试mpapi是否能正确处理使用其他请求参数, 例如timeout=3.

        正确结果为mpapi在使用requests相应的接口时原封不动的进行了
        kwargs的传递

        """
        mocker.patch.object(
            self.mpapi.session,
            'request',
            wraps=self.mpapi.session.request
        )
        self.mpapi.request(method, httpbin(method.lower()), **request_params)

        request_params.setdefault("allow_redirects", False)
        request_params.setdefault("timeout", settings.TIMEOUT)

        self.mpapi.session.request.assert_called_once_with(
            method,
            httpbin(method.lower()),
            params=self.mpapi._prepare_param_dict(None),
            **request_params
        )

    @pytest.mark.parametrize('status_code', [300, 400, 505])
    def test_status_error(self, httpbin, status_code):
        if status_code in settings.RETRY_STATUS_FORCELIST:
            return

        result = self.mpapi.get(httpbin('status/{}'.format(status_code)))

        assert result.is_failed
        assert result.errcode == status_code

    @pytest.mark.parametrize('status_code', settings.RETRY_STATUS_FORCELIST)
    def test_default_retry(self, httpbin, status_code, max_retries_time):
        start = time.time()

        with pytest.raises(RequestException):
            self.mpapi.get(httpbin('status/{}'.format(status_code)))

        end = time.time()
        assert end - start >= max_retries_time

    def test_get_timeout(self, httpbin):
        with pytest.raises(RequestException, match=r'timed out'):
            self.mpapi.get(httpbin('delay/0.1'), timeout=0.05)


@pytest.mark.usefixtures('response_builder')
class TestAuthExpired:

    def test_when_set_auth_update_callback(self,
                                           mp_access_token, auth_expired_ret):
        auth_update = mock.Mock()
        mpapi_instance = mpapi.formp(
            mp_access_token,
            auth_update_callback=auth_update
        )
        mpapi_instance.session.request = mock.Mock(
            return_value=self.response(text=auth_expired_ret)
        )
        result = mpapi_instance.get('/')

        auth_update.assert_called_once_with()
        assert result.errcode in settings.AUTH_EXPIRED_CODES

    def test_notset_auth_update_callback(self,
                                         mp_access_token, auth_expired_ret):
        mpapi_instance = mpapi.formp(mp_access_token)
        mpapi_instance.session.request = mock.Mock(
            return_value=self.response(text=auth_expired_ret)
        )
        result = mpapi_instance.get('/')

        assert result.errcode in settings.AUTH_EXPIRED_CODES

    def test_when_auth_notbeen_update(self,
                                      mp_access_token, auth_expired_ret):
        auth_update = mock.Mock(return_value=mp_access_token)
        mpapi_instance = mpapi.formp(
            mp_access_token,
            auth_update_callback=auth_update
        )
        mpapi_instance.session.request = mock.Mock(
            side_effect=[
                self.response(text=auth_expired_ret),
                self.response(text='{}')
            ]
        )
        result = mpapi_instance.get('/')

        auth_update.assert_called_once_with()
        assert result.errcode in settings.AUTH_EXPIRED_CODES

    def test_when_auth_update_failed(self,
                                     mp_access_token, auth_expired_ret):
        auth_update = mock.Mock(side_effect=Exception('auth update error'))
        auth_update.__name__ = 'auth_update'
        mpapi_instance = mpapi.formp(
            mp_access_token,
            auth_update_callback=auth_update
        )
        mpapi_instance.session.request = mock.Mock(
            side_effect=[
                self.response(text=auth_expired_ret),
                self.response(text='{}')
            ]
        )

        with pytest.raises(RequestException):
            mpapi_instance.get('/')

    def test_when_auth_update_succeed(self,
                                      mp_access_token, auth_expired_ret):
        auth_update = mock.Mock(return_value='new{}'.format(mp_access_token))
        mpapi_instance = mpapi.formp(
            mp_access_token,
            auth_update_callback=auth_update
        )
        mpapi_instance.session.request = mock.Mock(
            side_effect=[
                self.response(text=auth_expired_ret),
                self.response(text='{}')
            ]
        )

        result = mpapi_instance.get('/')
        assert not result.is_failed


class TestMpApiPath:

    @pytest.fixture(autouse=True, scope='class')
    def mpapi_fixture(self, request, mp_access_token, response_builder):
        request.cls.mpapi = mpapi.formp(mp_access_token)
        request.cls.mpapi.session.request = mock.Mock(
            return_value=self.response(text='{}')
        )

    @pytest.mark.parametrize('api_path', ['/user', 'user'])
    def test_relate_api_path(self, api_path):
        self.mpapi.get(api_path)
        self.mpapi.session.request.assert_called_with(
            'GET',
            u'https://api.weixin.qq.com/cgi-bin/user',
            allow_redirects=mock.ANY,
            params=mock.ANY,
            timeout=mock.ANY,
        )

    @pytest.mark.parametrize('api_path', [
        'http://ab.com',
        'http://abc.com/api'
    ])
    def test_abslute_api_path(self, api_path):
        self.mpapi.get(api_path)
        self.mpapi.session.request.assert_called_with(
            'GET',
            api_path,
            allow_redirects=mock.ANY,
            params=mock.ANY,
            timeout=mock.ANY,
        )


@pytest.mark.usefixtures('base_mpapi', 'response_builder')
class TestMpApiGroup:

    def test_group_with_same_api_path(self):
        group = self.mpapi.group(root_path=u'/api')
        group.session.request = mock.Mock(
            return_value=self.response(text='{}')
        )

        group.get('/user')
        group.session.request.assert_called_with(
            'GET',
            u'https://api.weixin.qq.com/cgi-bin/api/user',
            allow_redirects=mock.ANY,
            params=mock.ANY,
            timeout=mock.ANY,
        )

    def test_group_with_spec_headers(self, httpbin):
        group = self.mpapi.group(headers={"Group-Header": "group_header_val"})
        result = group.get(httpbin('headers'))

        assert result.headers['Group-Header'] == 'group_header_val'

    def test_group_with_spec_timeout(self, httpbin):
        self.mpapi.get(httpbin('delay/0.1'))

        group = self.mpapi.group(timeout=0.05)
        with pytest.raises(RequestException, match=r'timed out'):
            group.get(httpbin('delay/0.1'))

    def test_group_with_spec_authupdate(self, auth_expired_ret):
        auth_update = mock.Mock()
        group = self.mpapi.group(auth_update_callback=auth_update)
        group.session.request = mock.Mock(
            return_value=self.response(text=auth_expired_ret)
        )

        group.get('/user')
        auth_update.assert_called_once_with()
