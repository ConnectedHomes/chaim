import chaimlib.glue as glue
from chaimlib.wflambda import getWFKey

log = glue.log


class SlackSendFail(Exception):
    """
    Exception: failed to send back to Slack
    """
    pass


class SlackRcvFail(Exception):
    """
    Exception: failed to receive from Slack
    """
    pass


class InactiveUser(Exception):
    """
    Exception: User is inactive (unauthorised)
    """
    pass


class InvalidToken(Exception):
    """
    Exception: Application token (either slack or personal) was invalid
    """
    pass


class WavefrontMissing(Exception):
    """
    Exception: wavefront lambda registry is None
    """
    pass


def begin(rbody, context, isSlack=False):
    stage = glue.getDefaultValue(context, "stage", "dev")
    if stage == "dev":
        glue.setDebug()
    rbody = glue.addToReqBody(rbody, "stage", stage)
    apiid = glue.getDefaultValue(context, "apiId")
    rbody = glue.addToReqBody(rbody, "apiid", apiid)
    useragent = "slack" if isSlack else glue.getDefaultValue(context, "useragent", "unknown")
    rbody = glue.addToReqBody(rbody, "useragent", useragent)
    getWFKey(stage)
    return rbody


def bodyParams(btext):
    """
    Extract parameters from a query string and store them in a dictionary.

    :param btext: the query string.
    """
    retval = {}
    for val in btext.split('&'):
        k, v = val.split('=')
        retval[k] = v
    return retval
