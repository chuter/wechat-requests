# -*- coding: utf-8 -*-


from importlib import import_module

from wechat.compat import basestring
from . import MessageProcessException
from .context import Context
from .builder import XMLMessageBuilder


__all__ = ['new_pipeline']


class Pipeline(object):
    def __init__(self, handlers):
        self.handlers = []
        self.pre_process_handlers = []
        self.post_process_handlers = []

        self._load_handlers(handlers)

    def handle(self, raw_message, **kwargs):
        """
        Raises:
          MessageProcessException

        """
        # build message
        message = XMLMessageBuilder.parse(raw_message)

        # init context
        context = Context.new(**kwargs)
        context.defaults(message=message, raw_message=raw_message)

        # pre process
        self._pre_process(message, context)

        # process
        result = None
        for handler in self.handlers:
            try:
                result = handler.handle(message, context)
            except Exception as handle_error:
                raise MessageProcessException(
                    handle_error.__str__(),
                    handler=handler,
                    raw_message=context.raw_message
                )
            else:
                if result is not None:
                    context.set('handle_result', result)
                    context.set('handler', handler)

                    if not context.should_continue:
                        break

        # post process
        self._post_process(message, context)

        return result

    def _pre_process(self, message, context):
        for _pre_process_handler in self.pre_process_handlers:
            try:
                _pre_process_handler.pre_process(message, context)
            except Exception as handle_error:
                raise MessageProcessException(
                    handle_error.__str__(),
                    handler=_pre_process_handler,
                    raw_message=context.raw_message
                )

    def _post_process(self, message, context):
        for _post_process_handler in self.post_process_handlers:
            try:
                _post_process_handler.post_process(message, context)
            except Exception as handle_error:
                raise MessageProcessException(
                    handle_error.__str__(),
                    handler=_post_process_handler,
                    raw_message=context.raw_message
                )

    def _load_handlers(self, handlers):
        for _handler in handlers:
            if isinstance(_handler, basestring):
                _cls_path = _handler
                handler_module, handler_classname = _cls_path.rsplit('.', 1)
                module = import_module(handler_module)
                handler_class = getattr(module, handler_classname)
                handler_instance = handler_class()
            else:
                handler_instance = _handler

            if hasattr(handler_instance, 'handle'):
                self.handlers.append(handler_instance)

            if hasattr(handler_instance, 'pre_process'):
                self.pre_process_handlers.append(handler_instance)

            if hasattr(handler_instance, 'post_process'):
                self.post_process_handlers.append(handler_instance)


def new_pipeline(handlers):
    return Pipeline(handlers)
