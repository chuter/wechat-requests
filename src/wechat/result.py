# -*- encoding: utf-8


import logging
from bs4 import BeautifulSoup

from .compat import json, JSONDecodeError, bytes, str
from .settings import ENCODING


__all__ = ['build_from_response', 'build_from']


class RequestResult(object):

    _XML_SUCCESS_CODE = u'SUCCESS'

    def __init__(self, json, text, response=None):
        object.__setattr__(self, "_json_result", json or {})
        object.__setattr__(self, "_response", response)

        if isinstance(text, bytes):
            text = text.decode(ENCODING)
        object.__setattr__(self, "_text", text)

        if response is not None:
            object.__setattr__(self, "_request", response.request)
        else:
            object.__setattr__(self, "_request", None)

    @property
    def response(self):
        return self._response

    @property
    def request(self):
        return self._request

    @property
    def json(self):
        return self._json_result

    @property
    def text(self):
        """Content of the response, in unicode.
        """
        if self.response is None:
            return self._text
        else:
            return self.response.text

    @property
    def is_failed(self):
        return False

    def __getattr__(self, field_name):
        if isinstance(field_name, bytes):
            field_name = field_name.decode('utf-8')

        if not (field_name in self.json):
            raise AttributeError(field_name)

        return self.json.get(field_name)

    def __getitem__(self, field_name):
        if isinstance(field_name, bytes):
            field_name = field_name.decode('utf-8')

        return self.json.__getitem__(field_name)

    def __setattr__(self, k, v):
        raise AttributeError()


class RequestErrorResult(RequestResult):

    errcode_field = u'errcode'
    errmsg_field = u'errmsg'

    def __init__(self, json, text, response=None):
        super(RequestErrorResult, self).__init__(json, text, response)

    @property
    def is_failed(self):
        return True

    @property
    def errcode(self):
        return self.json[self.errcode_field]

    @property
    def errmsg(self):
        return self.json.get(self.errmsg_field, str(''))

    @classmethod
    def is_error_json(cls, _json):
        return _json.get(cls.errcode_field, 0) != 0

    @classmethod
    def build_error_json(cls, errcode, errmsg):
        return {
            cls.errcode_field: errcode,
            cls.errmsg_field: errmsg
        }


def _build_from_xml(xml_text, response):
    _json = {}
    soup = BeautifulSoup(xml_text, 'xml')
    for tag in soup.xml.children:
        k = tag.name
        if k is None:
            continue

        if isinstance(k, bytes):
            k = k.decode(ENCODING)

        _json[k] = tag.string

    if u'return_code' in _json:
        if _json[u'return_code'] != RequestResult._XML_SUCCESS_CODE:
            _json.update(RequestErrorResult.build_error_json(
                _json[u'return_code'],
                _json.get(u'return_msg', '')
            ))
            return RequestErrorResult(_json, xml_text, response)

    if u'result_code' in _json:
        if _json[u'result_code'] != RequestResult._XML_SUCCESS_CODE:
            _json.update(RequestErrorResult.build_error_json(
                _json.get(u'err_code', u'FAIL'),
                _json.get(u'err_code_des', '')
            ))
            return RequestErrorResult(_json, xml_text, response)

    return RequestResult(_json, xml_text, response)


def _build_from_json_str(json_text, response):
    if isinstance(json_text, bytes):
        json_text = json_text.decode(ENCODING)

    _json = json.loads(json_text)
    if RequestErrorResult.is_error_json(_json):
        return RequestErrorResult(_json, json_text, response)
    else:
        return RequestResult(_json, json_text, response)


def build_from(from_x, response=None):
    """build RequestResult from json,xml,plaintext in text or bytes type

    :param response: Requests Response object

    Returns:
      RequestResult object

    """
    if isinstance(from_x, dict):
        if RequestErrorResult.is_error_json(from_x):
            return RequestErrorResult(from_x, None, response)
        else:
            return RequestResult(from_x, None, response)

    if isinstance(from_x, bytes):
        from_x = from_x.decode(ENCODING)

    if isinstance(from_x, str):
        from_x = from_x.strip()

    if from_x.startswith(u'{') and from_x.endswith(u'}'):
        try:
            return _build_from_json_str(from_x, response)
        except JSONDecodeError as json_error: # noqa
            pass

    if from_x.startswith(u'<xml') and from_x.endswith(u'</xml>'):
        try:
            return _build_from_xml(from_x, response)
        except Exception as xml_error: # noqa
            pass

    return RequestResult({}, from_x, response)


def build_from_response(response):
    if response.status_code >= 300 or response.status_code < 200:
        errcode = response.status_code
        errmsg = response.text
        if errmsg.startswith('<html>') and errmsg.endswith('</thml>'):
            errmsg = ''

        error_json = RequestErrorResult.build_error_json(errcode, errmsg)
        return RequestErrorResult(error_json, response.text, response)

    try:
        ret_json = response.json()
    except ValueError as json_error: # noqa
        logging.getLogger('wechat').warning('JSON parse error', exc_info=True)
        return build_from(response.text, response)
    else:
        if RequestErrorResult.is_error_json(ret_json):
            return RequestErrorResult(ret_json, response.text, response)
        else:
            return RequestResult(ret_json, response.text, response)
