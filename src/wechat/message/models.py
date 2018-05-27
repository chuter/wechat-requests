# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup

from wechat.compat import basestring


class MessageTypes(object):
    def __init__(self):
        raise NotImplementedError()

    TEXT = u'text'
    LINK = u'link'
    IMAGE = u'image'
    EVENT = u'event'
    VOICE = u'voice'
    VIDEO = u'video'
    LOCATION = u'location'
    SHORT_VIDEO = u'shortvideo'


class MessageEventTypes(object):
    def __init__(self):
        raise NotImplementedError()

    VIEW = u'VIEW'
    SCAN = u'SCAN'
    CLICK = u'CLICK'
    LOCATION = u'LOCATION'
    SUBSCRIBE = u'subscribe'
    UNSUBSCRIBE = u'unsubscribe'


class XMLMessage(object):
    """微信消息，对应微信API接口中定义的XML，例如:
     <xml>
     <ToUserName><![CDATA[toUser]]></ToUserName>
     <FromUserName><![CDATA[fromUser]]></FromUserName>
     <CreateTime>1348831860</CreateTime>
     <MsgType><![CDATA[text]]></MsgType>
     <Content><![CDATA[this is a test]]></Content>
     <MsgId>1234567890123456</MsgId>
     </xml>

    可直接通过.ToUserName访问xml每个节点的值(为unicode)，该类为不可变的！！
    如果进行属性设置会得到异常

    例如如果raw_xml为上面的xml片段，那么：

    wm = WeixinMessage(raw_xml)
    xm.ToUserName 为 u'toUser'
    xm.CreateTime 为 u'1348831860'

    该实例提供所有类型的微信消息的通用属性：
    id, from_openid, to_openid和create_timestamp以及content
    可直接过wm.id, wm.from_openid, wm.to_openid和wm.create_timestamp
    以及wm.content来获取

    """
    def __init__(self, raw_xml):
        if not isinstance(raw_xml, basestring):
            raise TypeError('raw_xml not basestring type')

        object.__setattr__(self, 'soup', BeautifulSoup(raw_xml, 'xml'))
        object.__setattr__(self, 'raw', raw_xml)

    def __getattr__(self, key):
        if key in ['soup', 'raw']:
            return object.__getattribute__(self, key)

        if hasattr(self.soup, key) and getattr(self.soup, key) is not None:
            return getattr(self.soup, key).text
        else:
            return None

    def __setattr__(self, key, value):
        raise AttributeError(key)

    @property
    def type(self):
        return self.MsgType

    @property
    def content(self):
        if self.is_text():
            return self.Content
        elif self.is_event() and self.Event == 'CLICK':
            return self.EventKey
        else:
            return u'[{}]'.format(self.type)

    def is_event(self):
        return self.type == MessageTypes.EVENT

    def is_text(self):
        return self.type == MessageTypes.TEXT

    def is_image(self):
        return self.type == MessageTypes.IMAGE

    def is_voice(self):
        return self.type == MessageTypes.VOICE

    def is_video(self):
        return self.type == MessageTypes.VIDEO

    def is_shortvideo(self):
        return self.type == MessageTypes.SHORT_VIDEO

    def is_location(self):
        return self.type == MessageTypes.LOCATION

    def is_link(self):
        return self.type == MessageTypes.LINK

    def is_subscribe_event(self):
        return self.is_event() and self.Event == MessageEventTypes.SUBSCRIBE

    def is_unsubscribe_event(self):
        return self.is_event() and self.Event == MessageEventTypes.UNSUBSCRIBE

    def is_qrscene_subscribe_event(self):
        if self.is_subscribe_event():
            return self.EventKey.startswith('qrscene_')

        return False

    def is_scan_event(self):
        return self.is_event() and self.Event == MessageEventTypes.SCAN

    def is_click_event(self):
        return self.is_event() and self.Event == MessageEventTypes.CLICK

    @property
    def id(self):
        if self.is_event():
            return -1
        else:
            return int(self.MsgId)

    @property
    def from_openid(self):
        return self.FromUserName

    @property
    def to_openid(self):
        return self.ToUserName

    @property
    def create_timestamp(self):
        return int(self.CreateTime)

    def __str__(self):
        return self.raw
