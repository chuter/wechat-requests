# -*- encoding: utf-8


import pytest
import string

from wechat import sign


class TestRandomNonceStrGenerate:

    @pytest.mark.parametrize("length", [-1, 0])
    def test_invalid_length(self, length):
        with pytest.raises(ValueError):
            sign.random_nonce_str(length)

    @pytest.mark.parametrize("length", [5, 10, 20])
    def test_valid_length(self, length):
        nonce_str = sign.random_nonce_str(length)

        assert len(nonce_str) == length
        for char in nonce_str:
            assert char in (string.ascii_letters + string.digits)


@pytest.fixture(scope='module', autouse=True)
def signkey():
    return '192006250b4c09247ec02edce69f6a2d'


@pytest.fixture(scope='module', autouse=True)
def sign_params():
    return {
        "appid": "wxd930ea5d5a258f4f",
        "mch_id": "10000100",
        "device_info": "1000",
        "body": "test",
        "nonce_str": "ibuaiVcKdpRxkhJA"
    }


class TestSign:

    def test_md5_sign(self, signkey, sign_params):
        signed = sign.sign_for_pay(signkey, **sign_params)
        assert signed == '9A0A8659F005D6984697E2CA0A9CF3B7'

    def test_hmac_sha256_sign(self, signkey, sign_params):
        signed = sign.sign_for_pay(
            signkey,
            sign_type='HMAC-SHA256',
            **sign_params
        )
        assert signed == (
            '2C9DF1156522C0B2B03B4DBF3BCA5CACB602CBD5CA0F9E112458CF3E9855303B'
        )

    def test_with_invalid_signtype(self, signkey, sign_params):
        with pytest.raises(ValueError):
            sign.sign_for_pay(signkey, sign_type='invalid', **sign_params)

    def test_sign_for_jsapi(self):
        ret = sign.sign_for_jsapi(
            'sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg', # noqa
            'https://github.com/chuter/wechat-requests',
            nonce='KkXtuN0j0nsaJtH',
            timestamp=1526486834
        )

        assert ret['signature'] == 'ca92770171ac2afff6a247951b5e69a217cf34ff'
        assert ret['nonceStr'] == 'KkXtuN0j0nsaJtH'
        assert ret['timestamp'] == 1526486834
        assert ret['url'] == 'https://github.com/chuter/wechat-requests'

    def test_sign_with_defaults(self):
        ret = sign.sign_for_jsapi(
            'sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg', # noqa
            'https://github.com/chuter/wechat-requests',
        )

        assert len(ret['nonceStr']) == 16
        assert ret['timestamp'] is not None
