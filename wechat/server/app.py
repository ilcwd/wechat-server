# coding:utf8
"""

Author: ilcwd
"""
import hashlib
import logging
import re

import flask

from .utils import read_xml, utf8_str
from .response import nothing_reply
from .constants import MSG_TEXT, MSG_EVENT, G_WECHAT


__all__ = [
    'WechatApplication',
]

_logger = logging.getLogger(__name__)


class WechatApplication(object):
    def __init__(self, flask_app, url, server_token):
        """
        A wechat server.
        :param flask_app:
        :param url: register url to handle.
        :param server_token: wechat's server token.
        :return:
        """

        self.server_token = server_token
        self.error_reply = nothing_reply

        # registry to handle full matched text message
        self.text_match_registry = {}
        # registry to handle regular expression matched text message
        self.text_re_match_registry = []

        # registry to handle all msg
        self.msg_registry = {}

        # registry to handle all event
        self.event_registry = {}

        # register as a flask api
        flask_app.route(url, methods=['GET', 'POST'])(self._entry)

    def text(self, text, is_re=False):
        """
        Add a auto-reply for matching ``text``.
        :param text: str or list or tuple to match
        :param is_re: determine if ``text`` is a regular expression
        :return:
        """
        if not isinstance(text, (list, tuple)):
            text = [text]

        def _decro(func):
            for t in text:
                if is_re:
                    self.text_re_match_registry.append((re.compile(t), func))
                else:
                    self.text_match_registry[t] = func

            return func
        return _decro

    def event(self, event):
        if not isinstance(event, (list, tuple)):
            event = [event]

        def _decro(func):
            for t in event:
                self.event_registry[t] = func

            return func
        return _decro

    def message(self, msg):
        if not isinstance(msg, (list, tuple)):
            msg = [msg]

        def _decro(func):
            for t in msg:
                self.msg_registry[t] = func

            return func
        return _decro

    def _valid_signature(self):
        signature = utf8_str(flask.request.args.get('signature'))
        timestamp = utf8_str(flask.request.args.get('timestamp'))
        nonce = utf8_str(flask.request.args.get('nonce'))

        if not (signature and timestamp and nonce):
            _logger.info("invalid request from wechat server: %s", flask.request.url)
            return False

        # TODO: validate timestamp

        token = self.server_token
        tempstr = hashlib.sha1(''.join(sorted([token, timestamp, nonce]))).hexdigest()

        return tempstr == signature

    def _validation_signature(self):
        if self._valid_signature():
            return utf8_str(flask.request.args['echostr'])
        else:
            return ""

    def _entry(self):
        # for connecting
        if flask.request.args.get('echostr'):
            return self._validation_signature()

        # unauthorized request from wechat(or attacker)
        if not self._valid_signature():
            return ''

        data = flask.request.data

        try:
            msg = read_xml(data)
        except Exception:
            _logger.error("invalid data from wechat: %s", repr(data))
            return self.error_reply()

        # register into g
        flask.g.wechat = msg

        return self.default_hanlder()

    def default_hanlder(self):
        msg = flask.g.wechat
        msg_type = msg.get('MsgType')

        # text
        if msg_type == MSG_TEXT:
            content = msg.get('Content')

            if content in self.text_match_registry:
                text_func = self.text_match_registry[content]
                return text_func()

            for compiler, re_func in self.text_re_match_registry:
                # TODO: set matched groups as parameters
                if compiler.match(content):
                    return re_func()
        # event
        elif msg_type == MSG_EVENT:
            event = msg.get('Event')
            # all events
            if event in self.event_registry:
                return self.event_registry[event]()

        # all msg
        if msg_type in self.msg_registry:
            return self.msg_registry[msg_type]()

        return nothing_reply()





