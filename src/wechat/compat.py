# -*- coding: utf-8 -*-

# flake8: noqa

import sys

_ver = sys.version_info

is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)


try:
    import simplejson as json
except ImportError:
    import json
    JSONDecodeError = None
else:
    JSONDecodeError = json.errors.JSONDecodeError


if is_py2:
    if JSONDecodeError is None:
        JSONDecodeError = ValueError

    range = xrange
    unicode = unicode
    from urllib import quote as url_quote

elif is_py3:
    if JSONDecodeError is None:
        JSONDecodeError = json.decoder.JSONDecodeError

    range = range
    unicode = str
    from urllib.parse import quote as url_quote


from requests.compat import bytes, str, basestring