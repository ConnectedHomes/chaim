"""
lambda code to clean the chaim database of expired (30 days) keys.
The chaim api records issued keys to aid event tracing.
"""


import logging
import chaimlib.glue as glue
from chaimlib.permissions import Permissions
from chaimlib.wflambda import wfwrapper
from chaimlib.envparams import EnvParam

log = glue.log


@wfwrapper
def doCleanup(event, context, version):
    try:
        ep = EnvParam()
        spath = ep.getParam("SECRETPATH", True)
        environment = ep.getParam("environment", True)
        if spath is not False:
            pms = Permissions(spath, missing=True)
            dryrun = True if environment == "dev" else True
            tfr, afr = pms.cleanKeyMap(dryrun=dryrun)
            kmsg = "key" if afr == 1 else "keys"
            kmsg += " would be" if environment == "dev" else ""
            msg = "chaim cleanup v{}: {}/{} {} cleaned.".format(version, afr, tfr, kmsg)
            log.info(msg)
            glue.incMetric("cleanup")
            glue.ggMetric("cleanup.cleaned", afr)
            glue.ggMetric("cleanup.existing", tfr)
        else:
            emsg = "chaim cleanup: secret path not in environment"
            log.error(emsg)
            glue.incMetric("cleanup.error")
    except Exception as e:
        emsg = "chaim cleanup v{}: error: {}: {}".format(version, type(e).__name__, e)
        log.error(emsg)
        glue.incMetric("cleanup.error")


def cleanup(event, context):
    """
    This is the entry point for the cleanup cron

    cloudwatch cron expression: 23 4 * * ? *
    ( 04:23 every day )

    :param event: the AWS lambda event that triggered this
    :param context: the AWS lambda context for this
    """
    with open("version", "r") as vfn:
        version = vfn.read()
    ep = EnvParam()
    environment = ep.getParam("environment", True)
    if "dev" == environment:
        glue.setDebug()
    log.info("chaim cleanup v{}: entered".format(version))
    log.info("environment: {}".format(environment))
    glue.getWFKey(stage=environment)
    doCleanup(event, context, version)
