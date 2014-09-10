# coding:utf8
"""

Author: ilcwd
"""
import time
import hashlib
import os
import urllib
import random
import json

import flask
import werkzeug.test

from wechat.server.app import WechatApplication
from wechat.server import constants, utils, response


app = flask.Flask(__name__)
app.debug = True

WECHAT_TOKEN = 'a_random_token'
wechat = WechatApplication(app, '/wechat', WECHAT_TOKEN)


CLIENT = werkzeug.test.Client(app)

#######################################
# APIs
#######################################
@wechat.text('hello')
def handle_hello():
    return "hello"


@wechat.text('echo')
def echo_request():
    msg = flask.g.wechat
    return json.dumps(msg)


@wechat.text('.*regular.*', is_re=True)
def re_match():
    return 'matched'


@wechat.message(constants.MSG_TEXT)
def help_reply():
    """For cases that do not matched the above
    """
    return 'help msg'


@wechat.event(constants.EVENT_SUBSCRIBE)
def user_subscribe():
    """a new user subscribe your service.
    """
    from_user = flask.g.wechat['ToUserName']
    to_user = flask.g.wechat['FromUserName']
    return response.text_reply(from_user, to_user, "欢迎订阅！]]]><<--")


#######################################
# utilities
#######################################
def assert_equal(a, b):
    assert a == b, ("Expect `%s`, but `%s`." % (a, b))


def timestamp():
    return int(time.time())


def randomstr():
    return os.urandom(8).encode('hex')


def signature(token=WECHAT_TOKEN):
    ts = timestamp()
    nonce = randomstr()
    sign = hashlib.sha1(''.join(sorted(map(str, [token, ts, nonce])))).hexdigest()
    return ts, nonce, sign


def native_rpc(path, post=None, server_token=WECHAT_TOKEN):
    # werkzeug.test.Client donot set REMOTE_ADDR!
    environ_overrides = {'REMOTE_ADDR': '127.0.0.1'}

    method = 'POST' if post else 'GET'

    # sign request
    ts, nonce, sign = signature(server_token)
    path = path + '?' + urllib.urlencode({'timestamp': ts, 'nonce': nonce, 'signature': sign})

    # open request
    resp, status, headers = CLIENT.open(path=path, method=method,
                                        content_type='application/xml',
                                        data=post,
                                        environ_overrides=environ_overrides)

    # validation
    assert status.startswith('200'), status
    result = ''.join(resp)
    return result


class BaseRequest(object):
    _TEMPLATE = None
    def __init__(self):
        self.to_user = randomstr()
        self.from_user = randomstr()
        self.create_time = str(timestamp())
        self.msg_id = str(random.randint(0, 0xFFFFFFFFFFFFFFFF))

    def to_string(self):
        return self._TEMPLATE % self.__dict__


class EventRequest(BaseRequest):
    _TEMPLATE = """<xml><ToUserName><![CDATA[%(to_user)s]]></ToUserName>
<FromUserName><![CDATA[%(from_user)s]]></FromUserName>
<CreateTime>%(create_time)s</CreateTime>
<MsgType><![CDATA[%(msg_type)s]]></MsgType>
<Event><![CDATA[%(event)s]]></Event>
</xml>"""

    def __init__(self):
        super(EventRequest, self).__init__()
        self.msg_type = 'event'
        self.event = 'subscribe'


class TextRequest(BaseRequest):
    _TEMPLATE = """<xml><ToUserName><![CDATA[%(to_user)s]]></ToUserName>
<FromUserName><![CDATA[%(from_user)s]]></FromUserName>
<CreateTime>%(create_time)s</CreateTime>
<MsgType><![CDATA[%(msg_type)s]]></MsgType>
<Content><![CDATA[%(content)s]]></Content>
<MsgId>%(msg_id)s</MsgId>
</xml>"""

    def __init__(self, content):
        super(TextRequest, self).__init__()
        self.msg_type = 'text'
        self.content = content


#######################################
# Test cases
#######################################
def test_basic():
    # default empty response
    assert_equal(native_rpc('/wechat'), '')

    # invalid token
    assert_equal(native_rpc('/wechat', server_token='a_wrong_token'), '')

    # 404
    try:
        native_rpc('/wechat1', '')
    except AssertionError as e:
        assert e.args[0] == '404 NOT FOUND'
    else:
        assert False, "expect a 404 error"

    # echo hello
    request1 = TextRequest("hello")
    assert_equal(native_rpc('/wechat', request1.to_string()), 'hello')

    # echo request
    req_echo = TextRequest("echo")
    resp_echo = json.loads(native_rpc('/wechat', req_echo.to_string()))
    assert_equal(resp_echo['FromUserName'], req_echo.from_user)
    assert_equal(resp_echo['ToUserName'], req_echo.to_user)
    assert_equal(resp_echo['MsgId'], req_echo.msg_id)
    assert_equal(resp_echo['Content'], req_echo.content)
    assert_equal(resp_echo['CreateTime'], req_echo.create_time)

    # re matched
    req_re = TextRequest("this is an regular expression.")
    assert_equal(native_rpc('/wechat', req_re.to_string()), 'matched')

    # a subscribe event
    req_subscibe = EventRequest()
    resp = native_rpc('/wechat', req_subscibe.to_string())
    resp = utils.read_xml(resp)
    assert_equal(resp['Content'], u"欢迎订阅！]]]><<--")


def main():
    test_basic()

    print "fin"


if __name__ == '__main__':
    main()
