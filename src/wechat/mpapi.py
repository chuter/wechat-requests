# -*- encoding: utf-8


from copy import copy

from .api import Api
from .exceptions import RequestException
from .settings import AUTH_EXPIRED_CODES


__all__ = ['formp']


class MpApi(Api):

    AUTH_QS_KEY = 'access_token'

    def __init__(self, mp_access_token, auth_update_callback=None, **kwargs):
        if mp_access_token is None or len(mp_access_token) == 0:
            raise ValueError('access_token not valid')

        super(MpApi, self).__init__(**kwargs)

        self.__options = copy(kwargs)
        self._auth_token = mp_access_token
        self._auth_update_callback = auth_update_callback

    def _prepare_param_dict(self, params_dict):
        if params_dict is None:
            return {self.AUTH_QS_KEY: self._auth_token}
        else:
            params_dict[self.AUTH_QS_KEY] = self._auth_token
            return params_dict

    def _retry(self, result, method, url, params_dict, **kwargs):
        """
        When access token expired, update and then retry

        """
        if result.is_failed and result.errcode in AUTH_EXPIRED_CODES:
            new_auth_token = self._update_auth(result.response)
            if new_auth_token == self._auth_token:
                return result
            else:
                self._auth_token = new_auth_token
                params = self._prepare_param_dict(params_dict)
                return self._execute_request(
                    method,
                    url,
                    params_dict=params,
                    **kwargs
                )
        else:
            return result

    def group(self, **kwargs):
        cp_options = copy(self.__options)
        cp_options.update(kwargs)
        cp_options.setdefault('auth_update_callback', None)
        return self.__class__(self._auth_token, **cp_options)

    def _update_auth(self, response):
        if self._auth_update_callback is None:
            return self._auth_token

        try:
            new_auth_token = self._auth_update_callback()
        except Exception as auth_update_error:
            raise RequestException(
                u'Update auth failed use {}'.format(
                    self._auth_update_callback.__name__
                ),
                auth_update_error,
                response=response
            )
        else:
            return new_auth_token


def formp(mp_access_token, **kwargs):
    return MpApi(mp_access_token, **kwargs)
