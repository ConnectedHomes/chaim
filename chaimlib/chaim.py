import json
import requests
import chaimlib.glue as glue
from chaimlib.wflambda import getWFKey
from chaimlib.wflambda import incMetric
from slackclient import SlackClient

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


def sendToSlack(respondurl, msg):
    """
    Send messages back to Slack

    :param respondurl: the url to send back to
    :param msg: the text to send
    """
    try:
        if respondurl != "ignoreme":
            if len(msg) > 0:
                params = json.dumps(output(None, msg))
                r = requests.post(respondurl, data=params)
                if 200 != r.status_code:
                    emsg = "Failed to send back to initiating Slack channel"
                    emsg += ". status: {}, text: {}".format(r.status_code, r.text)
                    raise(SlackSendFail(emsg))
    except Exception as e:
        log.error("Send to Slack Failed: {}".format(e))


def sendSlackBot(apitoken, channel, msg, attach=None, title="\n*URL*\n"):
    """
    Send a private message to Slack, will appear under the 'SlackBot' channel for the user

    :param apitoken: The token to use to authenticate with slack
    :param channel: the slack username to send the message back to
    :param msg: the text to send to the slack channel
    :param attach: message attachments (see https://api.slack.com/docs/message-attachments)
    :param title: message title (see https://api.slack.com/docs/messages)
    """
    attachment = ""
    if attach is not None:
        attachment = makeAttachments(attach, title)
    sc = SlackClient(apitoken)
    res = sc.api_call("chat.postMessage", channel="@{}".format(channel), text=msg, attachments=attachment)
    return res


def output(err, res=None, attachments=None):
    """
    will return json formatted output to the caller

    :param err: error text or exception or None
    :param res: the message to send, will be bound up in a json formatted object
    :param attachments: any message attachments
    """
    ret = {
        'response_type': 'ephemeral',
        'statusCode': '400' if err else '200',
        'text': "{}".format(err) if err else "{}".format(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    if attachments is not None:
        ret["attachments"] = makeAttachments(attachments)
    return ret


def makeAttachments(attachments, pretext=None):
    """
    format message attachments for presentation to slack

    :param attachments: the attachment to format
    :param pretext: any additional text to show before the attachment
    """
    ret = [{
        "title": pretext,
        "title_link": attachments,
        "mrkdwn_in": ["text", "pretext"],
    }]
    return ret


def doCommand(cp, pms, verstr):
    """
    process the requested command

    :param cp: a CommandParse object
    :param pms: a Permissions object
    :param rdict: dictionary of user details from the incomming request
    """
    rdict = cp.requestDict()
    if cp.dolist:
        log.debug("account list requested")
        alist = pms.accountList()
        msg = "\n\n"
        for row in alist:
            msg += "{} {}\n".format(row[0], row[1])
        sendSlackBot(pms.slackapitoken, rdict["username"], msg)
        sendToSlack(rdict["responseurl"], "The SlackBot will send you the accounts list.")
        incMetric("slack.list")
    elif cp.dohelp:
        log.debug("help requested")
        sendSlackBot(pms.slackapitoken, rdict["username"], glue.usage())
        sendToSlack(rdict["responseurl"], "The SlackBot will help.")
        incMetric("slack.help")
    elif cp.doversion:
        log.debug("version request")
        sendToSlack(rdict["responseurl"], verstr)
        incMetric("slack.version")
    elif cp.dowhoskey:
        log.debug("whos key requested")
        msg = whosKey(pms, cp.whoskey)
        sendToSlack(rdict["responseurl"], msg)
        incMetric("slack.whoskey")
    elif cp.keyinit:
        log.debug("keyinit requested")
        rdict["apiid"] = cp.apiid
        msg = doKeyInit(rdict)
        sendToSlack(rdict["responseurl"], msg)
        incMetric("keyinit")
    elif cp.doinitshow:
        log.debug("initshow requested")
        rdict["apiid"] = cp.apiid
        msg = readKeyInit(rdict)
        sendToSlack(rdict["responseurl"], msg)
        incMetric("initshow")
    elif cp.doshowroles:
        log.debug("show roles requested")
        roledict = pms.roleAliasDict()
        msg = ""
        for ra in roledict:
            msg += "\n{}:\t{}".format(ra, roledict[ra])
        sendToSlack(rdict["responseurl"], "```{}```".format(msg))
        incMetric("showroles")
    elif cp.docountusers:
        msg = pms.countLastSince(2)
        sendToSlack(rdict["responseurl"], "```{}```".format(msg))
        incMetric("countusers")
