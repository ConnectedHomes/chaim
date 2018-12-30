"""
chaim functions for both CLI and Slack
"""

import logging

log = logging.getLogger(__name__)


def getDefaultValue(xdict, key, default=""):
    ret = default
    if key in xdict:
        ret = xdict[key]
    return ret


def addToReqBody(rbody, key, val):
    ret = rbody
    if len(ret) > 0:
        ret += "&"
    ret += key
    ret += "="
    ret += str(val)
    return ret


def setDebug():
    log.setLevel(logging.DEBUG)
