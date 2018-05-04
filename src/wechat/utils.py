# -*- encoding: utf-8


from six import iteritems

from .compat import json, str
from .__version__ import __version__, __name__


__all__ = ['build_user_agent']


_USER_AGENT = None


def build_user_agent():
    global _USER_AGENT

    if _USER_AGENT is None:
        _USER_AGENT = '{}{}'.format(__name__, __version__)

    return _USER_AGENT


class Node(object):

    def __init__(self):
        pass

    def prettify(self):
        raise NotImplementedError('implement prettify in sub class')


class Root(Node):

    PRETTIFY_INDENT = ' ' * 2

    def __init__(self):
        self._kvnodes = []

    def append(self, child):
        self._kvnodes.append(child)
        return self

    def prettify(self):
        out = [u'<xml>']
        for child in self._kvnodes:
            out.append(u'{}{}'.format(self.PRETTIFY_INDENT, child.prettify()))
        out.append(u'</xml>')
        return u'\n'.join(out)


class KVNode(Node):

    def __init__(self, key, value):
        self.key = key
        if type(value) in (dict, list):
            _value_str = json.dumps(value, ensure_ascii=False)
            self._pretty_value = u'<![CDATA[{}]]>'.format(_value_str)
        else:
            self._pretty_value = str(value)

    def prettify(self):
        return u'<{key}>{value}</{key}>'.format(
            key=self.key,
            value=self._pretty_value
        )


def serialize_dict_to_xml(**kwargs):
    root = Root()
    for k, v in iteritems(kwargs):
        if v is None:
            continue
        root.append(KVNode(k, v))

    return root.prettify()
