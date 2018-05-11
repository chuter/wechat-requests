# -*- encoding: utf-8

import re

from .compat import url_quote, bytes
from .api import Api
from . import settings


__all__ = ['get_mp_access_token', 'web_auth']


class MpOuthApi(Api):

    IMMUTABLE_FIELDS = frozenset(['_appid', '_secret'])

    def __init__(self, appid, secret, **kwargs):
        if appid is None or secret is None:
            raise ValueError('appid or secret')

        object.__setattr__(self, '_appid', appid)
        object.__setattr__(self, '_secret', secret)

        super(MpOuthApi, self).__init__(**kwargs)

    def _prepare_param_dict(self, params_dict):
        complete_params = {
            "appid": self._appid,
            "secret": self._secret
        }
        complete_params.update(params_dict or {})
        return complete_params

    def _retry(self, result, method, url, params_dict, **kwargs):
        if result.errcode != -1:
            return

        return self._execute_request(method, url, params_dict, **kwargs)


def get_mp_access_token(appid, secret, **kwargs):
    """
    Raises:
      RequestException
    """

    api = MpOuthApi(appid, secret, **kwargs)
    return api.get('/token', grant_type='client_credential')


_web_auth_api = Api()
_web_auth_api._base_url = u'https://api.weixin.qq.com/sns/'


class WebAuth(object):
    SCOPE_SNSAPI_BASE = 'snsapi_base'
    SCOPE_SNSAPI_USERINFO = 'snsapi_userinfo'

    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def build_authgrant_url(appid, redirect_uri, state=None,
                            scope=SCOPE_SNSAPI_USERINFO):
        if state is not None:
            if re.match('^[0-9a-zA-Z]*$', state) is None:
                raise ValueError('state')
            if len(state) > 128:
                raise ValueError('state')

        if isinstance(redirect_uri, bytes):
            redirect_uri = redirect_uri.decode('utf-8')

        if redirect_uri.find(u':') > 0:
            redirect_uri = url_quote(redirect_uri, '')

        return (
            u'https://{}/connect/oauth2/authorize?appid={}&redirect_uri={}&'
            u'response_type=code&scope={}&state={}#wechat_redirect'.format(
                settings.OAUTH_HOST,
                appid,
                redirect_uri,
                scope,
                state
            )
        )

    @classmethod
    def get_access_token(cls, appid, secret, code):
        return _web_auth_api.get(
            u'oauth2/access_token',
            appid=appid,
            secret=secret,
            code=code,
            grant_type='authorization_code'
        )

    @classmethod
    def refresh_access_token(cls, appid, refresh_token):
        return _web_auth_api.get(
            u'oauth2/refresh_token',
            appid=appid,
            refresh_token=refresh_token,
            grant_type='refresh_token'
        )

    @classmethod
    def get_user_info(cls, openid, access_token, lang='zh_CN'):
        return _web_auth_api.get(
            u'userinfo',
            openid=openid,
            access_token=access_token,
            lang=lang
        )


web_auth = WebAuth
