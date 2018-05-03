# -*- coding: utf-8 -*-

import sys

_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
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

elif is_py3:
    if JSONDecodeError is None:
        JSONDecodeError = json.decoder.JSONDecodeError


from requests.compat import bytes, str # noqa