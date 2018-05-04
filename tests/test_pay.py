# -*- encoding: utf-8

import pytest
import mock

from bs4 import BeautifulSoup

from wechat import pay, settings
from wechat.result import build_from_response


"""
Use `sandbox <https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=23_4>`_ to text

""" # noqa


@pytest.fixture(scope='module', autouse=True)
def pay_signkey():
    return 'dummy_pay_signkey'


@pytest.fixture(scope='module', autouse=True)
def mch_id():
    return 'dummy_mchid'


@pytest.fixture(scope='class')
def wxpay(request, mp_appid, mch_id, pay_signkey, fake_response):
    pay_instance = pay.for_merchant(mp_appid, mch_id, pay_signkey)
    patched_execute_request = mock.Mock(
        return_value=build_from_response(fake_response(text='<xml></xml>'))
    )
    pay_instance._execute_request = patched_execute_request

    request.cls.pay = pay_instance


@pytest.mark.usefixtures("wxpay")
class TestPay:

    @pytest.mark.parametrize('method', [
        'unifiedorder', 'orderquery', 'closeorder', 'refund', 'refundquery'
    ])
    def test_add_default_params(self, mp_appid, mch_id, pay_signkey, method):
        api = getattr(self.pay, method)
        api(out_trade_no='dummy_out_trade_no')

        call_args = self.pay._execute_request.call_args
        send_body = None
        for arg in call_args:
            if type(arg) is dict and 'data' in arg:
                send_body = arg['data']
                break

        soup = BeautifulSoup(send_body, 'xml')
        assert soup.appid.text == mp_appid
        assert soup.mch_id.text == mch_id
        assert len(soup.nonce_str.text) == settings.SIGN_NONCE_STR_LEN
        assert len(soup.sign.text) > 16

    @pytest.mark.parametrize('method', ['unifiedorder', 'refund'])
    def test_use_set_default_params(self, method):
        api = getattr(self.pay, method)
        api(out_trade_no='trade_no', appid='fake_app_id', mch_id='fake_mchid')

        call_args = self.pay._execute_request.call_args
        send_body = None
        for arg in call_args:
            if type(arg) is dict and 'data' in arg:
                send_body = arg['data']
                break

        soup = BeautifulSoup(send_body, 'xml')
        assert soup.appid.text == 'fake_app_id'
        assert soup.mch_id.text == 'fake_mchid'
