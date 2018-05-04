Wechat Requests
=========================

**To make it easier to requests Wechat/Weixin API(mp, pay, etc.)**


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