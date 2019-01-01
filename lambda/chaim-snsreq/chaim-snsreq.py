import chaimlib.glue as glue
import chaimlib.chaim as chaim
from chaimlib.envparams import EnvParam
from chaimlib.permissions import Permissions
from chaimlib.commandparse import CommandParse

log = glue.log


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
            emsg, kdict = chaim.buildCredentials(pms, rdict)
        except Exception as e:
            emsg = "doSnsReq error: {}: {}".format(type(e).__name__, e)
            log.error(emsg)
            chaim.sendToSlack(rdict["responseurl"], emsg)


def snsreq(event, context):
    """This is the entry point for the SNS chaim handler

    :param event: the AWS lambda event that triggered this
    :param context: the AWS lambda context for this
    """
    with open("version", "r") as vfn:
        version = vfn.read()
    msg = event['Records'][0]['Sns']['Message']
    rbody = chaim.begin(msg, context, True)
    ep = EnvParam()
    environment = ep.getParam("environment", True)
    verstr = "chaim-snsreq-" + environment + " " + version
    log.info(verstr + " entered.")
    log.debug("sns req: {}".format(rbody))
    doSnsReq(rbody, context, verstr, ep, environment)
