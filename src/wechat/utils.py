# -*- encoding: utf-8


from .__version__ import __version__, __name__

__all__ = ['DEFAULT_HEADERS']


_USER_AGENT = None


def build_user_agent():
    global _USER_AGENT

    if _USER_AGENT is None:
        _USER_AGENT = '{}{}'.format(__name__, __version__)

    return _USER_AGENT


DEFAULT_HEADERS = {
    'User-Agent': build_user_agent()
}
