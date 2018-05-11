# -*- encoding: utf-8

import pytest

from wechat.compat import str, url_quote, unicode
from wechat.result import build_from_response
from wechat import web_auth
from wechat.auth import _web_auth_api, WebAuth
from wechat import settings


@pytest.fixture
def patch_request(mocker, mp_appid, mp_secret, fake_response):
    patched_request_execute = mocker.MagicMock(
        return_value=build_from_response(
            fake_response(text='')
        )
    )
    mocker.patch.object(
        _web_auth_api,
        '_execute_request',
        patched_request_execute
    )
    return patched_request_execute


class TestOAuth:

    def test_get_access_token(self, mocker, mp_appid,
                              mp_secret, patch_request):
        web_auth.get_access_token(mp_appid, mp_secret, 'fake_code')
        patch_request.assert_called_once_with(
            'GET',
            'https://api.weixin.qq.com/sns/oauth2/access_token',
            params_dict={
                "grant_type": "authorization_code",
                "appid": mp_appid,
                "secret": mp_secret,
                "code": "fake_code"
            },
            allow_redirects=False,
            timeout=mocker.ANY
        )

    def test_refresh_access_token(self, mocker, mp_appid, patch_request):
        web_auth.refresh_access_token(mp_appid, 'fake_refresh_token')
        patch_request.assert_called_once_with(
            'GET',
            'https://api.weixin.qq.com/sns/oauth2/refresh_token',
            params_dict={
                "grant_type": "refresh_token",
                "appid": mp_appid,
                "refresh_token": "fake_refresh_token"
            },
            allow_redirects=False,
            timeout=mocker.ANY
        )

    def test_get_user_info(self, mocker, mp_appid,
                           mp_access_token, patch_request):
        web_auth.get_user_info('fake_openid', mp_access_token, lang='zh_CN')
        patch_request.assert_called_once_with(
            'GET',
            'https://api.weixin.qq.com/sns/userinfo',
            params_dict={
                "openid": "fake_openid",
                "access_token": mp_access_token,
                "lang": "zh_CN"
            },
            allow_redirects=False,
            timeout=mocker.ANY
        )


class TestOauthGranUrlBuilder:

    @pytest.mark.parametrize('state', [
        'abc123 ',
        ' abc123',
        'a' * 129,
    ])
    def test_with_invalid_state(self, mp_appid, state):
        with pytest.raises(ValueError, match='state'):
            web_auth.build_authgrant_url(mp_appid, '', state=state)

    @pytest.mark.parametrize('redirect_uri', [
        str('http://www.chuter.io'),
        b'http://www.chuter.io',
    ])
    def test_redirecturi_both_bytes_str(self, mp_appid, redirect_uri):
        oauth_url = web_auth.build_authgrant_url(mp_appid, redirect_uri)

        if isinstance(redirect_uri, bytes):
            redirect_uri = redirect_uri.decode('utf-8')

        assert oauth_url == (
            u'https://{}/connect/oauth2/authorize?'
            u'appid={}&redirect_uri={}&'
            u'response_type=code&scope={}&state=None#wechat_redirect'.format(
                settings.OAUTH_HOST,
                mp_appid,
                url_quote(redirect_uri, ''),
                WebAuth.SCOPE_SNSAPI_USERINFO
            )
        )

    def test_already_quote_redirecturi(self, mp_appid):
        dummy_redirect_uri = url_quote(unicode('http://www.chuter.io'), '')
        oauth_url = web_auth.build_authgrant_url(mp_appid, dummy_redirect_uri)
        assert oauth_url == (
            u'https://{}/connect/oauth2/authorize?'
            u'appid={}&redirect_uri={}&'
            u'response_type=code&scope={}&state=None#wechat_redirect'.format(
                settings.OAUTH_HOST,
                mp_appid,
                dummy_redirect_uri,
                WebAuth.SCOPE_SNSAPI_USERINFO
            )
        )
