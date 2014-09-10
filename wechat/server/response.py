# coding:utf8
"""

Author: ilcwd
"""
import time

from .utils import safe_cdata


TEXT_XML = r"""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
</xml>
"""

IMAGE_XML = r"""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[%s]]></MediaId>
</Image>
</xml>
"""

VOICE_XML = r"""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[voice]]></MsgType>
<Voice>
<MediaId><![CDATA[%s]]></MediaId>
</Voice>
</xml>
"""

VIDEO_XML = r"""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[video]]></MsgType>
<Video>
<MediaId><![CDATA[%s]]></MediaId>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
</Video>
</xml>
"""

NEWS_XML = r"""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>%s</ArticleCount>
<Articles>
%s
</Articles>
</xml>
"""

NEWS_ARTICLE_XML = r"""<item>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>
"""


def timestamp():
    return int(time.time())


def nothing_reply():
    """Response empty data to wechat server to stop wechat from retrying request.
    """
    return ''


def text_reply(from_user, to_user, content):
    return TEXT_XML % (safe_cdata(to_user, 0), safe_cdata(from_user, 0), timestamp(), safe_cdata(content, 0))


def news_reply(from_user, to_user, articles):
    count = len(articles)
    xml_articles = []
    for title, desc, pic, url in articles:
        xml_articles.append(NEWS_ARTICLE_XML % (safe_cdata(title, 0), safe_cdata(desc, 0),
                                                safe_cdata(pic, 0), safe_cdata(url, 0)))

    return NEWS_XML % (
        safe_cdata(to_user, 0),
        safe_cdata(from_user, 0),
        timestamp(),
        count,
        ''.join(xml_articles)
    )


def main():
    pass


if __name__ == '__main__':
    main()
