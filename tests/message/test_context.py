# -*- encoding: utf-8


from wechat.message.context import Context


class TestContext:

    def test_set(self):
        ctx = Context.new(name='wechat', version='1.0.0')
        ctx.set('name', 'wechat-requests')
        assert ctx.get('name') == 'wechat-requests'

    def test_defaults(self):
        ctx = Context.new(name='wechat', version='1.0.0')
        ctx.defaults(name="wechat_", author='chuter')
        assert ctx.get('name') == 'wechat'
        assert ctx.get('author') == 'chuter'

    def test_defaults_with_context(self):
        ctx = Context.new(name='wechat', version='1.0.0')
        ctx.defaults(**Context.new(name="wechat_", author='chuter'))
        assert ctx.get('name') == 'wechat'
        assert ctx.get('author') == 'chuter'

    def test_extends(self):
        ctx = Context.new(name='wechat', version='1.0.0')
        ctx.extends(name="wechat-requests", author='chuter')
        assert ctx.get('name') == 'wechat-requests'
        assert ctx.get('author') == 'chuter'
        assert ctx.get('version') == '1.0.0'

    def test_extends_with_context(self):
        ctx = Context.new(name='wechat', version='1.0.0')
        ctx.extends(**Context.new(name="wechat-requests", author='chuter'))
        assert ctx.get('name') == 'wechat-requests'
        assert ctx.get('author') == 'chuter'
        assert ctx.get('version') == '1.0.0'
