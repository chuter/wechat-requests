# -*- encoding: utf-8


import re
import logging

from urllib3.util.retry import Retry

import requests
from requests.adapters import HTTPAdapter

from .result import build_from_response
from .compat import bytes
from .settings import (DEFAULT_HEADERS, TIMEOUT, RETRYS,
                       RETRY_BACKOFF_FACTOR, RETRY_STATUS_FORCELIST)


log = logging.getLogger(__name__)


def _build_retry_session(session=None):
    session = session or requests.Session()
    retry = Retry(
        total=RETRYS,
        read=RETRYS,
        connect=RETRYS,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_FORCELIST,
    )

    adapter = HTTPAdapter()
    adapter.max_retries = retry
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class Api(object):

    API_BASE_URL = u'https://api.weixin.qq.com/cgi-bin'

    def __init__(self, root_path=u'/', headers=DEFAULT_HEADERS,
                 timeout=TIMEOUT, **kwargs):
        self._base_url = self.API_BASE_URL + u''
        self._base_url = self._prepare_api_url(root_path)
        self._timeout = timeout
        self._session = _build_retry_session()

        self._init_session(headers)

    def request(self, method, api_path, params_dict=None, **kwargs):
        """
        Raises:
          RequestException

        """
        kwargs.setdefault('timeout', self._timeout)
        kwargs.setdefault('allow_redirects', False)

        url = self._prepare_api_url(api_path)
        params_dict = self._prepare_param_dict(params_dict)

        result = self._execute_request(
            method,
            url,
            params_dict=params_dict,
            **kwargs
        )

        if result.is_failed:
            retry_result = self._retry(
                result,
                method,
                url,
                params_dict,
                **kwargs
            )
            if retry_result is None:
                log.warn(u'{} retry result is None'.format(
                    self.__class__.__name__)
                )
                retry_result = result

            return retry_result
        else:
            return result

    def _retry(self, result, method, url, params_dict, **kwargs):
        """Override this function to check Api result and decide
        whether to retry.

        If no need to retry, return result param;

        Else, do retry request, and return the result;

        If return value is None, the request will return the result param
        as the retry result.

        """
        return result

    def _prepare_param_dict(self, params_dict):
        """Override this function in sub class to add request
        params, like add auth info...
        """
        return params_dict

    def get(self, api_path, timeout=None, **params):
        return self.request(
            'GET',
            api_path,
            params_dict=params,
            timeout=timeout or self._timeout
        )

    def post(self, api_path, data=None, json=None, **params):
        return self.request(
            'POST',
            api_path,
            data=data,
            json=json,
            **params
        )

    @property
    def session(self):
        return self._session

    def _init_session(self, headers):
        if headers is not None:
            self._session.headers.update(headers)

        if headers != DEFAULT_HEADERS:
            self._session.headers.update(DEFAULT_HEADERS)

    def _prepare_api_url(self, api_path):
        if isinstance(api_path, bytes):
            api_path = api_path.decode('utf-8')

        if u'://' in api_path:
            return api_path

        uri = u'{}/{}'.format(self._base_url, api_path)
        return re.sub('(?<!:)//[/]?', '/', uri)

    def _execute_request(self, method, url, params_dict=None, **kwargs):
        response = self._session.request(
            method,
            url,
            params=params_dict,
            **kwargs
        )

        return build_from_response(response)
