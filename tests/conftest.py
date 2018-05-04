# -*- encoding: utf-8

import pytest

from wechat.compat import json
from wechat import settings
from .compat import urljoin, range


@pytest.fixture(scope="session", autouse=True)
def mp_access_token(request):
    return 'dummy_mp_account_access_token'


@pytest.fixture(scope='session', autouse=True)
def mp_appid(request):
    return 'dummy_mp_appid'


@pytest.fixture(scope='session', autouse=True)
def mp_secret(request):
    return 'dummy_mp_secret'


def prepare_url(value):
    # Issue #1483: Make sure the URL always has a trailing slash
    httpbin_url = value.url.rstrip('/') + '/'

    def inner(*suffix):
        return urljoin(httpbin_url, '/'.join(suffix))

    return inner


@pytest.fixture
def httpbin(httpbin):
    return prepare_url(httpbin)


@pytest.fixture
def httpbin_secure(httpbin_secure):
    return prepare_url(httpbin_secure)


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
            return json.loads(self.text)
        except:  # noqa: E722
            raise ValueError()


@pytest.fixture(scope='class')
def response_builder(request):
    def builder(cls, status_code=None, text=None):
        return FakeResponse(status_code, text)

    request.cls.response = builder


@pytest.fixture(scope='session', autouse=True)
def fake_response():
    def builder(status_code=None, text=None):
        return FakeResponse(status_code, text)

    return builder


@pytest.fixture(scope='session')
def max_retries_time():
    total_time = 0.0
    for i in range(settings.RETRYS):
        total_time += settings.RETRY_BACKOFF_FACTOR * (2 ^ i)
    return total_time


@pytest.fixture(scope='session', params=settings.AUTH_EXPIRED_CODES)
def auth_expired_ret(request):
    return '''{{
        "errcode": {request.param},
        "errmsg": "auth expired"
    }}'''.format(request=request)
