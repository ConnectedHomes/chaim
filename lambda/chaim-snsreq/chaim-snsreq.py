import chaimlib.glue as glue
import chaimlib.chaim as chaim
from slackclient import SlackClient
from chaimlib.envparams import EnvParam
from chaimlib.commandparse import CommandParse

log = glue.log


def doSnsReq(rbody, context, version):
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
    log.info("chaim cleanup v{}: entered".format(version))
    log.info("environment: {}".format(environment))
    log.debug("sns req: {}".format(rbody))
    doSnsReq(rbody, context, version)
