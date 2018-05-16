# -*- encoding: utf-8

"""
微信开放平台的公众号消息加密解密实现

具体文档参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1434696670

"""

import base64
import string
import random
import hashlib
import time
import struct
from Crypto.Cipher import AES
import socket

from bs4 import BeautifulSoup

from wechat.utils import serialize_dict_to_xml
from wechat.compat import unicode, str, is_py3
from .exceptions import (SignatureError, InvalidAESKeyError, EncryptError,
                         ReceiveMsgFormatError, InvalidSignature,
                         DecryptError, InvalidAppid)


__all__ = ['build_message_crypto_for']


class PKCS7Encoder(object):

    _BLODK_SIZE = 32

    @staticmethod
    def encode(text):
        if type(text) == unicode:
            text = text.encode('utf-8')

        text_length = len(text)

        amount_to_pad = (
            PKCS7Encoder._BLODK_SIZE - (text_length % PKCS7Encoder._BLODK_SIZE)
        )
        if amount_to_pad == 0:
            amount_to_pad = PKCS7Encoder._BLODK_SIZE

        pad = chr(amount_to_pad)
        return bytes(text + bytearray(pad * amount_to_pad, encoding='utf-8'))

    @staticmethod
    def decode(encoded):
        if is_py3:
            pad = encoded[-1]
        else:
            pad = ord(encoded[-1])

        if pad < 1 or pad > PKCS7Encoder._BLODK_SIZE:
            return encoded
        else:
            return encoded[:-pad]


def _sign(token, timestamp, nonce, encrypt):
    """
    用SHA1算法生成安全签名

    Args:
      token: 票据
      timestamp: 时间戳
      nonce: 随机字符串
      encrypt: 密文

    Returns:
      安全签名

    Raises:
      SignatureError

    """

    sortlist = []
    for field in [token, timestamp, nonce, encrypt]:
        if type(field) == unicode:
            field = field.encode('utf-8')
        sortlist.append(field)
    sortlist.sort()

    try:
        return hashlib.sha1(b''.join(sortlist)).hexdigest()
    except Exception as error:
        raise SignatureError(error)


class MsgCrypt(object):
    """
    微信开放平台的公众号消息加密解密实现

    Args:
      token: 消息校验Token
      aes_key: 消息加解密Key
      appid: AppID

    Raises:
      InvalidAESKeyError

    """

    _ENCODING = 'utf-8'

    mode = AES.MODE_CBC
    _RANDOM_STR_LEN = 16

    def __init__(self, token, aes_key, appid):
        try:
            self.key = base64.b64decode(aes_key + '=')
            assert len(self.key) == 32
        except Exception as error:
            raise InvalidAESKeyError(error)

        self.token = token
        self.appid = appid

    def encrypt(self, msg, nonce=None, timestamp=None):
        """
        对发送的微信消息进行加密

        Args:
          msg: 微信消息
          nonce: 随机串, 如果缺省会生成新的随机串
          timestamp: 时间戳, 如果缺省使用当前时间

        Returns:
          加密后的消息密文(unicode)

        Raises:
          SignatureError: 签名失败
          EncryptError: 加密失败

        """

        if isinstance(msg, unicode):
            msg = msg.encode(self._ENCODING)

        encryped_msg = self.__encrypt(msg)

        if nonce is None:
            nonce = self._create_random_str()
        if timestamp is None:
            timestamp = int(time.time())

        if type(timestamp) == int:
            timestamp = str(timestamp)

        signature = _sign(self.token, timestamp, nonce, encryped_msg)
        return serialize_dict_to_xml(
            Encrypt=encryped_msg,
            MsgSignature=signature,
            TimeStamp=timestamp,
            Nonce=nonce
        )

    def decrypt(self, receive_str, signature, timestamp, nonce):
        """
        对收到的微信信息进行解密
        场景为微信平台向指定url进行POST请求

        Args:
          receive_str: 收到的待解密的消息内容(对应POST中的数据)
          signature: 签名串(包含在请求URL参数(msg_signature)中)
          timestamp: 时间戳(包含在请求URL参数中)
          nonce: 随机串(包含在请求URL参数中)

        Returns:
          消息原文(unicode)

        Raises:
          ReceiveWXMsgFormatError: 收到的微信消息格式错误
          SignatureError: 签名失败
          InvalidSignature: 签名验证失败
          DecryptError: 解密失败
          InvalidAppid: appid验证失败

        """

        try:
            _soup = BeautifulSoup(receive_str, 'xml')
            encryped_msg = _soup.Encrypt.text.encode(self._ENCODING)
        except Exception:
            raise ReceiveMsgFormatError('can not parse:{}'.format(
                receive_str
            ))
        else:
            if type(timestamp) == int:
                timestamp = str(timestamp)

            signature_check = _sign(self.token, timestamp, nonce, encryped_msg)
            if signature != signature_check:
                raise InvalidSignature('{} != {}'.format(
                    signature_check,
                    signature
                ))

            return self.__decrypt(encryped_msg)

    def __encrypt(self, text):
        """
        进行实际加密操作

        Args:
          text: 需要加密的明文

        Returns:
          加密后的密文

        Raises:
          EncryptError

        """

        _bytes = bytes(
            bytearray(self._create_random_str(), self._ENCODING) +
            struct.pack("I", socket.htonl(len(text))) +
            text +
            bytearray(self.appid, self._ENCODING)
        )

        _bytes = PKCS7Encoder.encode(_bytes)
        cryptor = AES.new(self.key, self.mode, self.key[:self._RANDOM_STR_LEN])
        try:
            ciphertext = cryptor.encrypt(_bytes)
            return base64.b64encode(ciphertext)
        except Exception as error:
            raise EncryptError(error)

    def __decrypt(self, text):
        """
        进行实际的解密处理, 解密后需要删除明文中进行补位的字符

        Args:
          text: 密文

        Returns:
          原文(unicode)

        Raises:
          DecryptError: 解密失败
          InvalidAppid: appid验证失败

        """

        try:
            cryptor = AES.new(
                self.key,
                self.mode,
                self.key[:self._RANDOM_STR_LEN]
            )
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception:
            raise DecryptError()

        try:
            # 去掉补位字符
            plain_text = PKCS7Encoder.decode(plain_text)
            content = plain_text[self._RANDOM_STR_LEN:]
            xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
            xml_content = content[4:xml_len + 4]
            from_appid = content[xml_len + 4:]
        except Exception as error:
            raise DecryptError(error)
        else:
            if from_appid.decode(self._ENCODING) != self.appid:
                raise InvalidAppid('{} != {}'.format(from_appid, self.appid))

            return xml_content.decode(self._ENCODING)

    def _create_random_str(self):
        random_chars = random.sample(
            string.ascii_letters + string.digits,
            self._RANDOM_STR_LEN
        )
        return ''.join(random_chars)


def build_message_crypto_for(token, aes_key, appid):
    return MsgCrypt(token, aes_key, appid)
