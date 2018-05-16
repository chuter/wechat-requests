# -*- encoding: utf-8


import re
import mock
import pytest

from wechat.message import build_message_crypto_for
from wechat.message.exceptions import InvalidSignature, InvalidAppid

from bs4 import BeautifulSoup


@pytest.fixture(scope='module', autouse=True)
def token():
    return 'faketoken'


@pytest.fixture(scope='module', autouse=True)
def aes_key():
    return 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG'


@pytest.fixture(scope='module', autouse=True)
def timestamp():
    return 1409735669


@pytest.fixture(scope='module', autouse=True)
def appid():
    return 'wx2c2769f8efd9abc2'


@pytest.fixture(scope='module', autouse=True)
def nonce():
    return '1320562132'


@pytest.fixture(scope='module', autouse=True)
def receive_xml():
    return u"""<xml>
<ToUserName>ToUserName></ToUserName>
<FromUserName>FromUserName</FromUserName>
<CreateTime>1519387094</CreateTime>
<MsgType>text</MsgType>
<MsgId>-1</MsgId>
<Content>just a (汉字) test</Content>
</xml>""".encode('utf-8')


@pytest.fixture(scope='module', autouse=True)
def crypted_message():
    return """<xml>
<ToUserName><![CDATA[ToUserName]]></ToUserName>
<FromUserName><![CDATA[FromUserName]]></FromUserName>
<CreateTime>1409735669</CreateTime>
<Encrypt><![CDATA[uK+DOe54WRa31zp4IZ9wn2nmmyGW/Zp2lWg8s66DsPJDn4lq9Vl8ExMoUAYffJZhVNnMOay4ggAp3RGHteCKVU7krd8BUnoCcaOLyqbl36FxJWffWiOl6Xv4Xdb5fmQKnvG9swv4eXpTlH+L96SUa1C0dRofRC6tHJDHMNPuCun1R2UvQJRAcwoTIqwoHPMqJTehW3ttrohjeqaS7W9Nln3kufTmbwtyaYdwxUPP6agbc0KDGe3NzVGCQooAEmgOxQJW7kp2Rw6P7mLx2Mvr46bpiB6BFtDcZgnrto7/BqHzyCk50FPLl1BQDH2SgTkOzirV5XExAt1p+uuDSBo0Hw==]]></Encrypt>
</xml>"""


class TestMsgCrypto:

    def test_crypto_randomstr(self, token, aes_key, appid):
        crypto = build_message_crypto_for(token, aes_key, appid)
        random_str = crypto._create_random_str()

        assert re.match(r'^[0-9a-zA-Z]{16}$', random_str) is not None

    def test_encrypt(self, token, aes_key, timestamp, appid,
                     nonce, receive_xml):
        crypto = build_message_crypto_for(token, aes_key, appid)
        crypto._create_random_str = mock.Mock(
            return_value='FbpmyUzSlPYw1K7D'
        )

        encrypt_xml = crypto.encrypt(
            receive_xml,
            nonce=nonce,
            timestamp=timestamp
        )

        encrypt_soup = BeautifulSoup(encrypt_xml, 'xml')
        assert encrypt_soup.Encrypt.text == (
            u'uK+DOe54WRa31zp4IZ9wn2nmmyGW/Zp2lWg8s66DsPJDn4lq9Vl8ExMoUAYffJZh'
            u'VNnMOay4ggAp3RGHteCKVU7krd8BUnoCcaOLyqbl36FxJWffWiOl6Xv4Xdb5fmQK'
            u'nvG9swv4eXpTlH+L96SUa1C0dRofRC6tHJDHMNPuCun1R2UvQJRAcwoTIqwoHPMq'
            u'JTehW3ttrohjeqaS7W9Nln3kufTmbwtyaYdwxUPP6agbc0KDGe3NzVGCQooAEmgO'
            u'xQJW7kp2Rw6P7mLx2Mvr46bpiB6BFtDcZgnrto7/BqHzyCk50FPLl1BQDH2SgTkO'
            u'zirV5XExAt1p+uuDSBo0Hw=='
        )
        assert encrypt_soup.MsgSignature.text == (
            u'1f4874576de4a1ad6e860ec3b4aa09158897b784'
        )
        assert int(encrypt_soup.TimeStamp.text) == timestamp
        assert encrypt_soup.Nonce.text == nonce

    def test_encrypt_for_default_params(self, token, aes_key,
                                        appid, receive_xml):
        crypto = build_message_crypto_for(token, aes_key, appid)
        encrypt_xml = crypto.encrypt(receive_xml)

        encrypt_soup = BeautifulSoup(encrypt_xml, 'xml')
        assert re.match(
            r'^[0-9a-zA-Z]{16}$',
            encrypt_soup.Nonce.text
        ) is not None
        assert encrypt_soup.TimeStamp.text is not None

    def test_decrypt(self, token, aes_key, timestamp, appid,
                     nonce, receive_xml, crypted_message):
        crypto = build_message_crypto_for(token, aes_key, appid)
        signature = '1f4874576de4a1ad6e860ec3b4aa09158897b784'
        message_bytes = crypto.decrypt(
            crypted_message,
            signature,
            timestamp,
            nonce
        )

        assert message_bytes == receive_xml

    def test_decrypt_with_invalid_signature(self, token, aes_key, timestamp,
                                            nonce, appid, crypted_message):
        crypto = build_message_crypto_for(token, aes_key, appid)
        signature = 'fakesignature'

        with pytest.raises(InvalidSignature):
            crypto.decrypt(
                crypted_message,
                signature,
                timestamp,
                nonce
            )

    def test_decrypt_with_invalid_appid(self, token, aes_key, timestamp,
                                        nonce, crypted_message):
        crypto = build_message_crypto_for(token, aes_key, 'fakeappid')
        signature = '1f4874576de4a1ad6e860ec3b4aa09158897b784'

        with pytest.raises(InvalidAppid):
            crypto.decrypt(
                crypted_message,
                signature,
                timestamp,
                nonce
            )
