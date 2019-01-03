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
import chaimlib.glue as glue
import chaimlib.chaim as chaim
from chaimlib.envparams import EnvParam
from chaimlib.permissions import Permissions
from chaimlib.commandparse import CommandParse
from chaimlib.wflambda import wfwrapper

log = glue.log


@wfwrapper
def doSnsReq(rbody, context, verstr, ep, env):
    """The chaim sns handler hands off to this after obtaining the wavefront key

    :param rbody: the request body
    :param context: the AWS lambda context
    :param verstr: the full version string
    :param ep: an EnvParam object
    :param evn: the enviroment this is operating in
    """
    secretpath = ep.getParam("SECRETPATH", True)
    pms = Permissions(secretpath=secretpath, stagepath=env)
    cp = CommandParse(rbody, roledict=pms.roleAliasDict())
    if cp.docommand:
        log.debug("incoming command request")
        chaim.doCommand(cp, pms, verstr)
    else:
        rdict = cp.requestDict()
        try:
            log.debug("incoming sns request")
            kdict, rdict = chaim.buildCredentials(pms, rdict)
            if kdict is None:
                raise(Exception("Failed to build credentials."))
            cmsg = "\nCredentials OK. "
            cmsg += "The ChatBot will send a url for account "
            cmsg += "{} ".format(rdict["accountname"])
            cmsg += "- {} ".format(kdict["accountid"])
            cmsg += "with a role of {}\n".format(rdict["role"])
            chaim.sendToSlack(rdict["responseurl"], cmsg)
            umsg = "Account ID: {}".format(kdict["accountid"])
            if rdict["stage"] == "dev":
                umsg += "\nAccessKeyID: {}\n".format(kdict["accesskeyid"])
                umsg += "SecretKeyID: {}\n".format(kdict["secretkey"])
                umsg += "Session Token: {}\n".format(kdict["sessiontoken"])
            umsg += "\nLink {}\n".format(rdict["expiresstr"].lower())
            chaim.incMetric("key.sns")
            res = chaim.sendSlackBot(pms.slackapitoken, rdict["username"], umsg, kdict["url"],
                                     "{} {}".format(rdict["accountname"].upper(), rdict["role"]))
            if res['ok'] is False:
                emsg = "Sending login url to users private Slack Channel failed"
                emsg += ": {}".format(res)
                log.error(emsg)
                chaim.sendToSlack(rdict["responseurl"], emsg)
                raise(chaim.SlackSendFail(emsg))
        except Exception as e:
            emsg = "doSnsReq error: {}: {}".format(type(e).__name__, e)
            log.error(emsg)
            chaim.sendToSlack(rdict["responseurl"], emsg)


def snsreq(event, context):
    """This is the entry point for the SNS chaim handler

    :param event: the AWS lambda event that triggered this
    :param context: the AWS lambda context for this
    """
    log.info("context: {}".format(context))
    ep = EnvParam()
    environment = ep.getParam("environment", True)
    apiid = ep.getParam("APIID", True)
    with open("version", "r") as vfn:
        version = vfn.read()
    body = event['Records'][0]['Sns']['Message']
    rbody = chaim.begin(body, environment, "slack", apiid)
    verstr = "chaim-snsreq-" + environment + " " + version
    log.info(verstr + " entered.")
    log.debug("sns req: {}".format(rbody))
    doSnsReq(rbody, context, verstr, ep, environment)
