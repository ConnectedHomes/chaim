import base64
import json
import requests
from slackclient import SlackClient
import chaimlib.glue as glue
from chaimlib.permissions import IncorrectCredentials
from chaimlib.utils import Utils
from chaimlib.wflambda import getWFKey
from chaimlib.wflambda import incMetric

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


def whosKey(pms, key):
    """
    map a chaim issued key to a slack (or CLI) user

    :param pms: Permissions object
    :param key: the key to map
    """
    ut = Utils()
    row = pms.whosKey(key)
    if len(row) > 0:
        log.debug("extracting key")
        key = row[0][0]
        log.debug("key got {}".format(key))
        log.debug("extracting expires")
        expires = row[0][1]
        whenat = ut.expiresAt(expires)
        log.debug("expires got {}".format(expires))
        log.debug("extracting name")
        username = row[0][2]
        log.debug("name got {}".format(username))
        log.debug("extracting account")
        account = row[0][3]
        log.debug("account got {}".format(account))
        msg = "\n\nKey {}".format(key)
        msg += "\nIssued to: {}".format(username)
        msg += "\nfor account: {}".format(account)
        msg += "\nExpires at: {}\n\n".format(whenat)
    else:
        msg = "Key not found"
    return msg


def doKeyInit(rdict, pms):
    """
    generate and set user token

    :param rdict: a dictionary of user details built from the incomming request
    """
    try:
        log.debug("keyinit incoming request: {}".format(rdict))
        if not pms.userActive(rdict["username"]):
            raise InactiveUser("{} is not an active user.".format(rdict["username"]))
        log.debug("doKeyInit User {} is ACTIVE".format(rdict["username"]))
        log.debug("doKeyInit checking token")
        if not pms.checkToken(rdict["incomingtoken"], rdict["username"]):
            raise InvalidToken("slack access token is invalid")
        log.debug("doKeyInit slack token check passed ok")
        expiredays = 30 if rdict["stage"] != "dev" else 1
        ut = Utils()
        uuid, expires = ut.newUserToken(expiredays)
        if pms.updateUserToken(rdict["username"], uuid, expires):
            expat, xstr, bstr = buildInitOutputStr(uuid, expires, rdict)
            msg = "New Chaim Credentials Expire {}\n{}\n```{}```".format(expat, xstr, bstr)
        else:
            msg = "Failed to write a new user token, sorry."
            raise InvalidToken(msg)
    except Exception as e:
        msg = "doKeyInit error: {}: {}".format(type(e).__name__, e)
        log.error(msg)
        return msg
    return msg


def readKeyInit(rdict, pms):
    try:
        log.debug("keyinit incoming request: {}".format(rdict))
        log.debug("checking inactive user")
        if not pms.userActive(rdict["username"]):
            raise InactiveUser("{} is not an active user.".format(rdict["username"]))
        log.debug("checking user token {}, {}".format(rdict["incomingtoken"], rdict["username"]))
        if not pms.checkToken(rdict["incomingtoken"], rdict["username"]):
            raise InvalidToken("slack access token is invalid")
        log.debug("asking for previous token")
        token, expires = pms.readUserToken(rdict["username"])
        expat, xstr, bstr = buildInitOutputStr(token, expires, rdict)
        msg = "Chaim Credentials Expire {}\n{}\n```{}```".format(expat, xstr, bstr)
    except Exception as e:
        msg = "readKeyInit error: {}: {}".format(type(e).__name__, e)
        log.error(msg)
        return msg
    return msg


def buildInitOutputStr(token, expires, rdict):
    ut = Utils()
    expa = ut.expiresAt(expires)
    bstr = ""
    xstr = "```"
    xstr = glue.addToOutStr(xstr, "api", rdict["apiid"])
    bstr = glue.addToReqBody(bstr, "api", rdict["apiid"])
    xstr = glue.addToOutStr(xstr, "username", rdict["username"])
    bstr = glue.addToReqBody(bstr, "username", rdict["username"])
    xstr = glue.addToOutStr(xstr, "usertoken", token)
    bstr = glue.addToReqBody(bstr, "usertoken", token)
    xstr = glue.addToOutStr(xstr, "expires", expires)
    bstr = glue.addToReqBody(bstr, "expires", expires)
    xstr = glue.addToOutStr(xstr, "stage", rdict["stage"])
    bstr = glue.addToReqBody(bstr, "stage", rdict["stage"])
    xstr = glue.addToOutStr(xstr, "region", "eu-west-1")
    bstr = glue.addToReqBody(bstr, "region", "eu-west-1")
    xstr += "```\n"
    butf8 = bstr.encode('utf8')
    benc = base64.urlsafe_b64encode(butf8)
    bstr = "```chaim -j " + str(benc) + "```"
    return expa, xstr, bstr


def buildCredentials(pms, rdict, noUrl=False):
    emsg = kdict = None
    try:
        ut = Utils()
        zstart = ut.getNow()
        userid = checkUserAndToken(pms, rdict)
        pms.lastupdated(userid, stamp=zstart, cli=noUrl)
        slackTimeStamp("token check", zstart, rdict, ut)
        accountid = checkUserAllowed(pms, rdict)
        slackTimeStamp("user authorised", zstart, rdict, ut)
        if accountid == rdict["accountname"]:
            rdict["accountname"] = pms.derivedaccountname
    except Exception as e:
        emsg = "buildCredentials error: {}: {}".format(type(e).__name__, e)
        log.error(emsg)
    return [emsg, kdict]


def checkUserAllowed(pms, rdict):
    user = rdict["username"]
    account = rdict["accountname"]
    role = rdict["role"]
    # everyone is allowed to use the ChaimDownloader role in the connectedhome-dev account
    if "ChaimDownloader" == role and "connectedhome-dev" == account:
        allowed = True
        accountid = "572871073281"
    else:
        allowed, accountid = pms.userAllowed(user, account, role)
    if not allowed:
        emsg = "user {} is not allowed to access {} at role {}".format(user, account, role)
        log.error(emsg)
        raise(IncorrectCredentials(emsg))
    log.info("user {} is allowed to access {} at role {}".format(user, account, role))
    return accountid


def checkUserAndToken(pms, rdict):
    if not pms.userActive(rdict["username"]):
        emsg = "{} is not an active user.".format(rdict["username"])
        log.error(emsg)
        raise(IncorrectCredentials(emsg))
    log.debug("User {} is ACTIVE".format(rdict["username"]))
    log.debug("Ensuring user exists for permissions check.")
    userid = pms.checkIDs("awsusers", "name", "User", rdict["username"], True)
    if userid is None:
        emsg = "user {} does not exist in chaim.".format(rdict["username"])
        log.error(emsg)
        raise(IncorrectCredentials(emsg))
    log.debug("user {}/{} exists".format(rdict["username"], userid))
    if not pms.checkToken(rdict["incomingtoken"], rdict["username"]):
        emsg = "user {} supplied an invalid token".format(rdict["username"])
        log.error(emsg)
        raise(IncorrectCredentials(emsg))
    log.debug("token check passed")
    return userid


def slackTimeStamp(msg, start, rdict, ut):
    if log.getEffectiveLevel() == 10:
        # debug mode so send timestamp to slack
        znow = ut.getNow()
        zlen = znow - start
        smsg = "{0:.2f} . {}".format(zlen, msg)
        sendToSlack(rdict["responseurl"], smsg)
