# -*- coding: utf-8 -*-

"""
This module handles import compatibility issues between Python 2 and
Python 3.
"""

# flake8: noqa

import sys

_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)


if is_py2:
    from urlparse import urlparse, parse_qs, parse_qsl, urljoin
    range = xrange

elif is_py3:
    from urllib.parse import urlparse, parse_qs, parse_qsl, urljoin
    range = range
