import chaimlib.glue as glue
import chaimlib.chaim as chaim
from chaimlib.envparams import EnvParam
from chaimlib.permissions import Permissions
from chaimlib.commandparse import CommandParse

log = glue.log


def doSnsReq(rbody, context, verstr, ep, env):
    secretpath = ep.getParam("SECRETPATH", True)
    pms = Permissions(secretpath=secretpath, stagepath=env)
    roled = pms.roleAliasDict()
    cp = CommandParse(rbody, roledict=roled)
    if cp.docommand:
        chaim.doCommand(cp, pms, verstr)
    else:
        pass


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
