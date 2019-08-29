#
# Copyright (c) 2018, Centrica Hive Ltd.
#
#     This file is part of chaim.
#
#     chaim is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     chaim is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with chaim.  If not, see <http://www.gnu.org/licenses/>.
#
import base64
import json
import requests
from slackclient import SlackClient
import chalicelib.glue as glue
from chalicelib.assumedrole import AssumedRole
from chalicelib.permissions import DataNotFound
from chalicelib.permissions import IncorrectCredentials
from chalicelib.snsclient import SnsClient
from chalicelib.stsclient import StsClient
from chalicelib.utils import Utils
from chalicelib.wflambda import getWFKey
from chalicelib.wflambda import incMetric

log = glue.log


class CredentialsGenerationFail(Exception):
    """Failed to generate full credentials"""
    pass


class UrlGenerationFail(Exception):
    """Failed to generate a url"""
    pass


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


def begin(rbody, environment="dev", useragent="unknown", apiid=""):
    log.debug("begin entry: {}, {}, {}, {}".format(rbody, environment, useragent, apiid))
    stage = environment
    apiid = apiid
    if stage == "dev":
        glue.setDebug()
    rbody = glue.addToReqBody(rbody, "stage", stage)
    rbody = glue.addToReqBody(rbody, "apiid", apiid)
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
        if respondurl is None:
            emsg = "SendToSlack: Error no respond url: {}".format(msg)
            raise SlackRcvFail(emsg)
        if respondurl != "ignoreme":
            if len(msg) > 0:
                params = json.dumps(output(None, msg))
                r = requests.post(respondurl, data=params)
                if 200 != r.status_code:
                    emsg = "Failed to send back to initiating Slack channel"
                    emsg += ". status: {}, text: {}".format(r.status_code, r.text)
                    raise(SlackSendFail(emsg))
    except Exception as e:
        emsg = "sendToSlack: Error {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        raise


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
    rdict["username"] = pms.userNameFromSlackIds(rdict["teamid"], rdict["slackid"])
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
        msg = doKeyInit(rdict, pms)
        sendToSlack(rdict["responseurl"], msg)
        incMetric("keyinit")
    elif cp.doinitshow:
        log.debug("initshow requested")
        rdict["apiid"] = cp.apiid
        msg = readKeyInit(rdict, pms)
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
    elif cp.doidentify:
        msg = "Slack User: {} Slack Workspace ID: {} Slack UID: {}".format(cp.username, cp.teamid, cp.slackid)
        sendToSlack(rdict["responseurl"], msg)
        incMetric("slack.identify")


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
            msg = "New Chaim Credentials Expire {}\n{}\n{}".format(expat, xstr, bstr)
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
        msg = "Chaim Credentials Expire {}\n{}\n{}".format(expat, xstr, bstr)
    except Exception as e:
        msg = "readKeyInit error: {}: {}".format(type(e).__name__, e)
        log.error(msg)
        return msg
    return msg


def buildInitOutputStr(token, expires, rdict):
    log.debug("in buildInitOutputStr")
    ut = Utils()
    expa = ut.expiresAt(expires)
    bstr = ""
    xstr = "```"
    xstr = glue.addToOutStr(xstr, "api", rdict["apiid"])
    bstr = glue.addToReqBody(bstr, "api", rdict["apiid"])
    xstr = glue.addToOutStr(xstr, "slackid", rdict["slackid"])
    bstr = glue.addToReqBody(bstr, "slackid", rdict["slackid"])
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
    bstr = "```chaim -j " + benc.decode('utf8') + "```"
    return expa, xstr, bstr


def buildCredentials(pms, rdict, noUrl=False):
    emsg = kdict = None
    try:
        ut = Utils()
        zstart = ut.getNow()
        log.debug("buildCredentials: checking user and token")
        userid = checkUserAndToken(pms, rdict)
        log.debug("buildCredentials: updating last access stamp")
        pms.lastupdated(userid, stamp=zstart, cli=noUrl)
        log.debug("buildCredentials: updating slack")
        slackTimeStamp("token check", zstart, rdict, ut)
        log.debug("buildCredentials: checking user allowed")
        accountid = checkUserAllowed(pms, rdict)
        slackTimeStamp("user authorised", zstart, rdict, ut)
        if accountid == rdict["accountname"]:
            # if the original accountname was just the number
            # obtain the correct name
            rdict["accountname"] = pms.derivedaccountname
        ar, aro, rdict = startSTS(pms, rdict, accountid, ut, zstart)
        slackTimeStamp("role assumed", zstart, rdict, ut)
        kdict = getUrl(ar, aro, pms, rdict, noUrl, accountid)
    except Exception as e:
        emsg = "buildCredentials error: {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        raise(CredentialsGenerationFail(emsg))
    return [kdict, rdict]


def getUrl(ar, aro, pms, rdict, noUrl, accountid):
    kdict = None
    log.debug("asking for url for {} seconds (if requested)".format(rdict["duration"]))
    loginurl = "notset" if noUrl else ar.getLoginUrl(rdict["duration"])
    if loginurl is not False:
        creds = aro["Credentials"]
        kdict = {
            "accountid": accountid,
            "sectionname": rdict["accountname"],
            "accesskeyid": creds["AccessKeyId"],
            "secretkey": creds["SecretAccessKey"],
            "sessiontoken": creds["SessionToken"],
            "expiresstr": rdict["expiresstr"],
            "expires": rdict["expires"],
            "url": loginurl,
            "slackapitoken": pms.slackapitoken
        }
    else:
        emsg = "Failed to generate a login url"
        log.error(emsg)
        raise UrlGenerationFail(emsg)
    return kdict


def startSTS(pms, rdict, accountid, ut, zstart):
    aro = None
    try:
        log.debug("attempting sts")
        akey = pms.getEncKey("accesskeyid")
        skey = pms.getEncKey("secretkeyid")
        sname = rdict["username"]
        dur = rdict["duration"]
        role = rdict["role"]
        stsc = StsClient(accesskey=akey, secretkey=skey, sessionname=sname, duration=dur)
        rolearn = "arn:aws:iam::{}:role/{}".format(accountid, role)
        aro, xstr = stsc.assumeRoleStr(rolearn)
        log.debug("sts completed")
        slackTimeStamp("keys obtained", zstart, rdict, ut)
    except Exception as e:
        emsg = "startSTS error: {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        raise(DataNotFound(emsg))
    if aro is None:
        emsg = "failed to generate access keys for user {}".format(sname)
        emsg += " for account {}".format(rdict["accountname"])
        emsg += " at role {}".format(role)
        log.error(emsg)
        raise(DataNotFound(emsg))
    rdict["expires"], rdict["expiresstr"] = ut.expiresInAt(rdict["duration"])
    msg = "Key: {}".format(aro["Credentials"]["AccessKeyId"])
    msg += " issued to {}".format(sname)
    msg += " for account {}".format(rdict["accountname"])
    msg += " and role {}".format(role)
    log.info(msg)
    log.debug("Recording accesskeyid in db")
    pms.updateKeyMap(sname, accountid, aro["Credentials"]["AccessKeyId"], rdict["expires"])
    log.debug("starting assumed role object")
    try:
        ar = None
        ar = AssumedRole(aro)
    except Exception as e:
        emsg = "startSTS AssumedRole error: {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        raise(DataNotFound(emsg))
    return [ar, aro, rdict]


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
    lel = log.getEffectiveLevel()
    log.debug("log effective level: {}".format(lel))
    if lel == 10:
        # debug mode so send timestamp to slack
        znow = ut.getNow()
        zlen = znow - start
        smsg = "{0:.2f} . {1}".format(zlen, msg)
        log.debug("sending to slack {}".format(smsg))
        sendToSlack(rdict["responseurl"], smsg)


def snsPublish(topic, msg):
    sns = SnsClient()
    sns.publishToSns(topic, msg)


def testVPCInternetAccess():
    log.info("Sending a request to icanhazip.com")
    r = requests.get("http://icanhazip.com")
    log.info("Status code: {}".format(r.status_code))
    log.info("reply: {}".format(r.text))
