# -*- encoding: utf-8

from .utils import build_user_agent

# common
DEFAULT_HEADERS = {
    'User-Agent': build_user_agent()
}

TIMEOUT = 1

ENCODING = 'utf-8'

RETRYS = 3
RETRY_BACKOFF_FACTOR = 0.1
RETRY_STATUS_FORCELIST = frozenset([500, 502, 504])


# auth
AUTH_EXPIRED_CODES = frozenset([40014, 41001, 42001])

# pay
TRADE_TYPE_JSAPI = 'JSAPI'  # 公众号支付
TRADE_TYPE_NATIVE = 'NATIVE'  # 扫码支付
TRADE_TYPE_APP = 'APP'  # APP支付

SIGN_TYPE = 'MD5'
SIGN_NONCE_STR_LEN = 32
