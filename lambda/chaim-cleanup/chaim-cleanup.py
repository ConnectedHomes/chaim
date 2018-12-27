"""
lambda code to clean the chaim database of expired (30 days) keys.
The chaim api records issued keys to aid event tracing.
"""


import logging
import chaimlib.chaim as chaim
from chaimlib.permissions import Permissions
from chaimlib.wflambda import wfwrapper
from chaimlib.envparams import EnvParam

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
# log.setLevel(logging.INFO)


@wfwrapper
def doCleanup(event, context, version):
    try:
        ep = EnvParam()
        spath = ep.getParam("SECRETPATH", True)
        if spath is not False:
            pms = Permissions(spath, missing=True)
            tfr, afr = pms.cleanKeyMap()
            kmsg = "key" if afr == 1 else "keys"
            msg = "chaim cleanup v{}: {} {} cleaned.".format(version, afr, kmsg)
            log.info(msg)
            chaim.incMetric("cleanup")
            chaim.ggMetric("cleanup.cleaned", afr)
            chaim.ggMetric("cleanup.existing", tfr)
        else:
            emsg = "chaim cleanup: secret path not in environment"
            log.error(emsg)
            chaim.incMetric("cleanup.error")
    except Exception as e:
        emsg = "chaim cleanup v{}: error: {}: {}".format(version, type(e).__name__, e)
        log.error(emsg)
        chaim.incMetric("cleanup.error")


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
    log.debug("chaim cleanup v{}: entered".format(version))
    chaim.getWFKey(stage="dev")
    doCleanup(event, context, version)
