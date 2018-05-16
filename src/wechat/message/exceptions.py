# -*- coding: utf-8 -*-


class MessageProcessException(Exception):

    def __init__(self, *args, **kwargs):
        self.handler = kwargs.pop('handler', None)
        self.raw_message = kwargs.pop('raw_message', None)
        super(MessageProcessException, self).__init__(*args, **kwargs)


class MessageCryptoProcessError(Exception):
    """failed to process the encrypt or decrypt"""


class InvalidAESKeyError(MessageCryptoProcessError):
    pass


class SignatureError(MessageCryptoProcessError):
    pass


class InvalidSignature(MessageCryptoProcessError):
    pass


class ReceiveMsgFormatError(MessageCryptoProcessError):
    """receive message is not in the right format"""


class EncryptError(MessageCryptoProcessError):
    pass


class DecryptError(MessageCryptoProcessError):
    pass


class InvalidAppid(MessageCryptoProcessError):
    pass
