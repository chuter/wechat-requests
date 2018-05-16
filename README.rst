Wechat Requests
=========================

**To make it easier to requests Wechat/Weixin API(mp, pay, etc.)**

both for py3 and py2, test coverage >90%

Usage
-------------------------

Install
"""""""""""""""""""""""""

.. code-block:: bash

    pip install wechat-requests


MPApi
"""""""""""""""""""""""""

.. code-block:: python

    >>>from wechat import auth
    >>>r = auth.get_mp_access_token('your appid', 'your appsecret')
    >>>r.access_token
    'ACCESS_TOKEN'
    >>>r.json
    {u'access_token': u'ACCESS_TOKEN', u'expires_in': 7200}
    >>>r.text
    u'{"access_token":"ACCESS_TOKEN","expires_in":7200}'
    >>>from wechat import mpapi
    >>>mp = mpapi.formp(r.access_token)
    >>>user = mp.get('user/info', openid='o6_bmjrPTlm6_2sgVt7hMZOPfL2M')
    >>>user.is_failed
    False
    >>>user.headimgurl
    u'http://thirdwx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/0'


Pay
"""""""""""""""""""""""""
See `WeChat Pay DOC <https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_1>`_ for detail

.. code-block:: python

    >>>from wechat import pay
    >>>mppay = pay.for_merchant(mchid, signkey)
    >>>r = mppay.unifiedorder(\
    ...     body='test',
    ...     out_trade_no='20150806125346',
    ...     total_fee=88,
    ...     spbill_create_ip='123.12.12.123',
    ...     notify_url='http://www.weixin.qq.com/wxpay/pay.php'
    ...)
    >>>r.is_failed
    False
    >>>r.prepay_id
    u'wx201410272009395522657a690389285100'
    >>>r = mppay.orderquery(out_trade_no='20150806125346')
    >>>r.trade_state
    u'SUCCESS'


If visit api which need client cert:

.. code-block:: python

    >>>from wechat import pay
    >>>mppay = pay.for_merchant(mchid, signkey, client_cert='./apiclient_cert.pem', client_key='apiclient_key.pem')
    >>>r = mppay.refund(\
    ...     transaction_id='1217752501201407033233368018',
    ...     total_fee=88,
    ...     refund_fee=88
    ...)
    >>>r.refund_id
    u'2008450740201411110000174436'


WebOauth
"""""""""""""""""""""""""
See `WeChat DOC <https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842>`_ for detail


.. code-block:: python

    >>>from wechat import web_auth
    >>>web_auth.build_authgrant_url('APPID', 'http://redirect_to')
    u'https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE#wechat_redirect'
    >>>result = web_auth.get_access_token('APPID', 'SECRET', 'CODE')
    >>>result.access_token
    u'ACCESS_TOKEN'
    >>>user_result = web_auth.get_user_info('OPENID', result.access_token)
    >>>user_result.unionid
    u'o6_bmasdasdsad6_2sgVt7hMZOPfL'
    >>>refresh_result = web_auth.refresh_access_token('APPID', result.refresh_token)
    >>>refresh_result.refresh_token
    u'REFRESH_TOKEN'


Message Hanlde Pipeline
"""""""""""""""""""""""""
See `WeChat DOC <https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140453>`_ for detail

.. code-block:: python

    >>>from wechat.message import new_pipeline
    >>>message_pipeline = new_pipeline([handler_instance, 'your.handler.path'])
    >>>reply_message_bytes = message_pipeline.handle('receive xml message')
    >>>from wechat.message import XMLMessageBuilder
    >>>reply_message = XMLMessageBuilder.parse(reply_message_bytes)
    >>>reply_message.to_openid
    u'fromUser'


Message Crypto
"""""""""""""""""""""""""
See `WeChat DOC <https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1434696670>`_ for detail

.. code-block:: python

    >>>from wechat.message import build_message_crypto_for
    >>>crypto = build_message_crypto_for('TOKEN', 'AES_KEY', 'APPID')
    >>>crypto.encrypt('MESSAGE_XML')
    <xml>
    <ToUserName><![CDATA[ToUserName]]></ToUserName>
    <FromUserName><![CDATA[FromUserName]]></FromUserName>
    <CreateTime>1409735669</CreateTime>
    <Encrypt><![CDATA[uK+DOe54WRa31zp4IZ9wn2nmmyGW/Zp2lWg8s66DsPJDn4lq9Vl8ExMoUAYffJZhVNnMOay4ggAp3RGHteCKVU7krd8BUnoCcaOLyqbl36FxJWffWiOl6Xv4Xdb5fmQKnvG9swv4eXpTlH+L96SUa1C0dRofRC6tHJDHMNPuCun1R2UvQJRAcwoTIqwoHPMqJTehW3ttrohjeqaS7W9Nln3kufTmbwtyaYdwxUPP6agbc0KDGe3NzVGCQooAEmgOxQJW7kp2Rw6P7mLx2Mvr46bpiB6BFtDcZgnrto7/BqHzyCk50FPLl1BQDH2SgTkOzirV5XExAt1p+uuDSBo0Hw==]]></Encrypt>
    </xml>
    >>>crypto.decrypt('ENCRYPTED_MSG', 'SIGNATURE', 'timestamp', 'nonce')
    <xml>
    <ToUserName>ToUserName></ToUserName>
    <FromUserName>FromUserName</FromUserName>
    <CreateTime>1519387094</CreateTime>
    <MsgType>text</MsgType>
    <MsgId>-1</MsgId>
    <Content>just a (汉字) test</Content>
    </xml>


RequestResult
"""""""""""""""""""""""""

All api return RequestResult instance, it auto handle xml, json

take r for example:

- r.name or r['name']: to get wechat api return result field(both xml and json)
- r.text: to get raw wechat api returned body (unicode/py2, str/py3)
- r.response: Requests Response instance
- r.request: Requests PreparedRequest instance, for users to debug the
             low level request
- r.is_failed: whether wechat api raise error
- r.errcode: if r.is_failed
- r.errmsg: if r.is_failed, error message for man


Advanced
-------------------------

comming soon...


Feature Support
-------------------------

Wechat Requests is based on `requests <https://github.com/requests/requests>`_
and `urllib3 <https://github.com/shazow/urllib3>`_

*get*, *post* function surpports all ``requests`` surpport, like headers,
timeout, etc.


Documentation
------------------------

coming soon...


TODO
------------------------

* web oauth surpport
* wechat/wxpay third party platformcomponent api surpport
* wechat message processing pipeline

**will published in two weeks**