Wechat Server
====

A wechat server midware to handle request from (wechat) user and reply.


Test
----

	nosetests


Examples
----

	import flask

	from wechat.server import WechatApplication
	from wechat.server import constants, utils, response
	
	app = flask.Flask(__name__)
	app.debug = True

	WECHAT_TOKEN = '<your_wechat_token>'
	wechat = WechatApplication(app, '/wechat', WECHAT_TOKEN)


	CLIENT = werkzeug.test.Client(app)


	#######################################
	# APIs
	#######################################
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

