# -*- encoding: utf-8


import pytest

from wechat.result import build_from_response
from wechat.auth import MpOuthApi, get_mp_access_token


@pytest.mark.usefixtures('response_builder')
class TestAuth:

    def test_mp_auth_params(self, mocker, mp_appid, mp_secret):
        patched_request_execute = mocker.MagicMock(
            return_value=build_from_response(
                self.response(text=u'{"access_token": "fake token"}')
            )
        )
        mocker.patch.object(
            MpOuthApi,
            '_execute_request',
            patched_request_execute
        )
        get_mp_access_token(mp_appid, mp_secret)
        patched_request_execute.assert_called_once_with(
            'GET',
            'https://api.weixin.qq.com/cgi-bin/token',
            params_dict={
                "grant_type": "client_credential",
                "appid": mp_appid,
                "secret": mp_secret
            },
            allow_redirects=False,
            timeout=mocker.ANY
        )

    def test_mp_auth_retry(self, mocker, mp_appid, mp_secret):
        patched_request_execute = mocker.MagicMock(
            return_value=build_from_response(
                self.response(text=u'{"errcode": -1}')
            )
        )
        mocker.patch.object(
            MpOuthApi,
            '_execute_request',
            patched_request_execute
        )
        mocker.spy(MpOuthApi, '_execute_request')

        result = get_mp_access_token(mp_appid, mp_secret)

        assert result.errcode == -1
        assert patched_request_execute.call_count == 2

    def test_auth_appid_secret_immutable(self, mp_appid, mp_secret):
        outh = MpOuthApi(mp_appid, mp_secret)

        with pytest.raises(AttributeError):
            outh._appid = 'new appid'

        with pytest.raises(AttributeError):
            outh._secret = 'new secret'
