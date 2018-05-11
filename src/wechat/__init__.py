# -*- coding: utf-8 -*-

# flake8: noqa

from .__version__ import __version__
from .exceptions import RequestException
from .auth import web_auth

import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())