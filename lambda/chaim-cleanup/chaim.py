"""
chaim functions for both CLI and Slack
"""

import os
import logging
from permissions import Permissions
from envparams import EnvParam
from wflambda import get_registry

log = logging.getLogger(__name__)


def ggMetric(mname, val):
    """
    sets a gauge wavefront metric value
    """
    log.debug("gauge metric stage: dev")
    registry = get_registry()
    fname = "chaim." + os.environ["CHAIM_STAGE"] + "." + mname
    if registry is not None:
        gge = registry.gauge(fname)
        try:
            log.debug("gauge: {}: {}".format(fname, val))
            gge.set_value(int(val))
        except Exception as e:
            log.warning("gauge failed for {}: {}: {}".format(mname, type(e).__name__, e))
    else:
        log.warning("Failed to initialise the wavefront registry for: " + fname)
    return


def incMetric(mname):
    """
    increments a wavefront metric counter
    """
    log.debug("inc metric stage: dev")
    registry = get_registry()
    fname = "chaim." + os.environ["CHAIM_STAGE"] + "." + mname
    if registry is not None:
        counter = registry.counter(fname)
        try:
            log.debug("counter inc: {}".format(fname))
            counter.inc()
        except Exception as e:
            log.warning("inc failed for {}: {}: {}".format(mname, type(e).__name__, e))
    else:
        log.warning("Failed to initialise the wavefront registry for: " + fname)
    return


def getWFKey(stage="prod"):
    """
    retrieves the wavefront access key from the param store
    and populates the environment with it
    """
    try:
        secretpath = EnvParam.getParam("SECRETPATH", decode=True)
        pms = Permissions(secretpath, stagepath=stage + "/", missing=False)
        wfk = pms.getEncKey("wavefronttoken")
        os.environ["WAVEFRONT_API_TOKEN"] = wfk
        os.environ["CHAIM_STAGE"] = stage
        log.debug("getWFKey: stage: {}".format(os.environ["CHAIM_STAGE"]))
    except Exception as e:
        msg = "getWFKey error occurred: {}: {}".format(type(e).__name__, e)
        log.error(msg)
        raise


def getDefaultValue(dict, key, default=""):
    ret = default
    if key in dict:
        ret = dict[key]
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


def begin(rbody, context, isSlack=False):
    stage = getDefaultValue(context, "stage", "dev")
    if stage == "dev":
        setDebug()
    rbody = addToReqBody(rbody, "stage", stage)
    apiid = getDefaultValue(context, "apiId")
    rbody = addToReqBody(rbody, "apiid", apiid)
    useragent = "slack" if isSlack else getDefaultValue(context, "useragent", "unknown")
    rbody = addToReqBody(rbody, "useragent", useragent)
    getWFKey(stage)
    return rbody
