# -*- encoding: utf-8


from wechat.compat import json
from wechat import utils


class TestXmlSerialize:

    def test_empty_kwargs(self):
        xml_text = utils.serialize_dict_to_xml()
        assert xml_text == u'<xml>\n</xml>'

    def test_kwargs_onlywith_base_type(self):
        xml_text = utils.serialize_dict_to_xml(
            number=2,
            bool=False,
            bytes=bytes('bytes')
        )

        assert u'  <number>2</number>' in xml_text
        assert u'  <bool>False</bool>' in xml_text
        assert u'  <bytes>bytes</bytes>' in xml_text
        assert xml_text.startswith(u'<xml>')
        assert xml_text.endswith(u'</xml>')

    def test_kwargs_with_dict_type(self):
        _dict = {"bool": False, "number": 2, "bytes": 'bytes'}
        xml_text = utils.serialize_dict_to_xml(
            dict=_dict
        )

        assert xml_text == (
            u'<xml>\n'
            u'  <dict><![CDATA[{}]]></dict>\n'
            u'</xml>'
        ).format(json.dumps(_dict, ensure_ascii=False))
