# -*- encoding: utf-8


from .utils import build_user_agent


AUTH_EXPIRED_CODES = frozenset([40014, 41001, 42001])

DEFAULT_HEADERS = {
    'User-Agent': build_user_agent()
}

TIMEOUT = 1

ENCODING = 'utf-8'

RETRYS = 3
RETRY_BACKOFF_FACTOR = 0.1
RETRY_STATUS_FORCELIST = frozenset([500, 502, 504])
