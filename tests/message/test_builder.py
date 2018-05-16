# -*- encoding: utf-8


from wechat.message import XMLMessageBuilder


class TestXMLMsgParse:

    def test_textmsg_parse(self):
        message = XMLMessageBuilder.parse(
            """<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[this is a test]]></Content>
            <MsgId>1234567890123456</MsgId>
            </xml>
            """
        )

        assert message.ToUserName == u'toUser'
        assert message.to_openid == u'toUser'
        assert message.FromUserName == u'fromUser'
        assert message.from_openid == u'fromUser'
        assert message.is_text()
        assert message.content == u'this is a test'
        assert message.Content == u'this is a test'


class TestXMLMsgBuild:

    def test_text_replymsg_build(self, received_message_str):
        received_message = XMLMessageBuilder.parse(received_message_str)
        reply_xmlmsg_bytes = XMLMessageBuilder.build_reply_textmsg_for(
            received_message,
            'just a 汉字 reply'
        )

        reply_xmlmsg = XMLMessageBuilder.parse(reply_xmlmsg_bytes)
        assert reply_xmlmsg.to_openid == received_message.from_openid
        assert reply_xmlmsg.from_openid == received_message.to_openid
        assert reply_xmlmsg.content == u'just a 汉字 reply'
