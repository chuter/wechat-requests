# -*- encoding: utf-8


from .api import Api


__all__ = ['get_mp_access_token']


class OuthApi(Api):

    def __init__(self, appid, secret, **kwargs):
        if appid is None or secret is None:
            raise ValueError('appid or secret')

        object.__setattr__(self, '_appid', appid)
        object.__setattr__(self, '_secret', secret)

        super(OuthApi, self).__init__(**kwargs)

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

    def __setattr__(self, key, value):
        if key in ('_appid', '_secret'):
            raise AttributeError()

        object.__setattr__(self, key, value)


def get_mp_access_token(appid, secret, **kwargs):
    """
    Raises:
      RequestException
    """

    api = OuthApi(appid, secret, **kwargs)
    return api.get('/token', grant_type='client_credential')
