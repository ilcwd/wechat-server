# coding:utf8
"""

Author: ilcwd
"""

import xml.etree.cElementTree


def utf8_str(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    elif isinstance(s, str):
        return s

    return str(s)


def read_xml(xmlstr):
    """Simple xml to dict function.

    Aim for wechat request parsing.
    """
    if not xmlstr:
        return {}

    def _read_node(xmlnodes):
        _result = {}
        for item in xmlnodes:
            children = item.getchildren()
            if children:
                _result[item.tag] = _read_node(children)
            else:
                _result[item.tag] = item.text
        return _result

    return _read_node(xml.etree.cElementTree.fromstring(xmlstr))


def safe_cdata(s, wrap=True):
    s = utf8_str(s)

    s = s.replace(']]>', ']]]]><![CDATA[>')
    if wrap:
        return r"<![CDATA[%s]]>" % s

    return s


def main():

    x = """<xml><ToUserName><![CDATA[gh_073d2ed7bb43]]></ToUserName>
<FromUserName><![CDATA[oWCKZt5pOVeSlAsxKXR1wkK8OCYY]]></FromUserName>
<CreateTime>1409736394</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[f]]></Content>
<MsgId>6054771708411376215</MsgId>
</xml>
"""
    print read_xml(x)


if __name__ == '__main__':
    main()
