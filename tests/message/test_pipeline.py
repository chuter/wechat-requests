# -*- encoding: utf-8


import pytest
import mock

from wechat.compat import range

from wechat.message import new_pipeline, MessageProcessException


@pytest.fixture
def process_fail_handler(mocker):
    fake_handler = mocker.MagicMock()
    fake_handler.handle.side_effect = Exception('handle failed')
    return fake_handler


@pytest.fixture
def preprocess_fail_handler(mocker):
    fake_handler = mocker.MagicMock()
    fake_handler.pre_process.side_effect = Exception('preprocess failed')
    return fake_handler


@pytest.fixture
def postprocess_fail_handler(mocker):
    fake_handler = mocker.MagicMock()
    fake_handler.post_process.side_effect = Exception('postprocess failed')
    return fake_handler


class FakeHandler(object):

    def handle(self, message, context):
        pass


def fake_handlers(count, return_at):
    _handlers = []

    for i in range(count):
        fake_handler = mock.MagicMock()
        ret = i if return_at == i else None
        fake_handler.handle.return_value = ret
        fake_handler.pre_process.return_value = None
        fake_handler.post_process.return_value = None

        _handlers.append(fake_handler)

    return _handlers


class TestPipeline:

    def test_none_handlers(self, received_message_str):
        with pytest.raises(TypeError):
            new_pipeline(None)

    @pytest.mark.parametrize('empty_handlers', [[], ()])
    def test_empty_handlers(self, empty_handlers, received_message_str):
        pipeline = new_pipeline(empty_handlers)
        assert pipeline.handle(received_message_str) is None

    @pytest.mark.parametrize(
        ('handlers', 'return_value', 'execute_count', 'handlers_count'),
        [
            (fake_handlers(3, 0), 0, 1, 3),
            (fake_handlers(3, 1), 1, 2, 3),
            (fake_handlers(3, 2), 2, 3, 3),
        ]
    )
    def test_base(self, handlers, return_value, execute_count,
                  handlers_count, received_message_str):
        pipeline = new_pipeline(handlers)
        assert pipeline.handle(received_message_str) == return_value

        execute_handlers = handlers[:execute_count]
        for handler in execute_handlers:
            handler.pre_process.assert_called_once()

        not_execute_handlers = handler[execute_count:]
        for handler in not_execute_handlers:
            handler.pre_process.assert_not_called()

    def test_module_load(self, mocker, received_message_str):
        pipeline = new_pipeline([
            '{}.{}'.format(
                FakeHandler.__module__,
                FakeHandler.__name__
            )
        ])

        mocker.patch.object(
            pipeline.handlers[0],
            'handle',
            wraps=pipeline.handlers[0].handle
        )

        pipeline.handle(received_message_str)
        pipeline.handlers[0].handle.assert_called_once()

    def test_failed(self, process_fail_handler, received_message_str):
        not_execute_handlers = fake_handlers(3, 2)
        pipeline = new_pipeline([process_fail_handler] + not_execute_handlers)

        with pytest.raises(MessageProcessException):
            pipeline.handle(received_message_str)

    def test_pre_process_failed(self, mocker, preprocess_fail_handler,
                                received_message_str):
        fake_handler = FakeHandler()
        mocker.patch.object(
            fake_handler,
            'handle',
            wraps=fake_handler.handle
        )
        pipeline = new_pipeline([fake_handler, preprocess_fail_handler])

        with pytest.raises(MessageProcessException) as process_error:
            pipeline.handle(received_message_str)
            assert process_error.handler == preprocess_fail_handler

        fake_handler.handle.assert_not_called()

    def test_post_process_failed(self, mocker, postprocess_fail_handler,
                                 received_message_str):
        fake_handler = FakeHandler()
        mocker.patch.object(
            fake_handler,
            'handle',
            wraps=fake_handler.handle
        )
        pipeline = new_pipeline([fake_handler, postprocess_fail_handler])

        with pytest.raises(MessageProcessException) as process_error:
            pipeline.handle(received_message_str)
            assert process_error.handler == postprocess_fail_handler

        fake_handler.handle.assert_called_once()
