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
"""
lambda code to clean the chaim database of expired (30 days) keys.
The chaim api records issued keys to aid event tracing.
"""


import chalicelib.glue as glue
from chalicelib.permissions import Permissions
from chalicelib.wflambda import wfwrapper
from chalicelib.wflambda import getWFKey
from chalicelib.wflambda import incMetric
from chalicelib.wflambda import ggMetric
from chalicelib.envparams import EnvParam

log = glue.log


@wfwrapper
def doCleanup(event, context, version):
    try:
        ep = EnvParam()
        spath = ep.getParam("SECRETPATH", True)
        environment = ep.getParam("environment", True)
        if spath is not False:
            pms = Permissions(spath, missing=True)
            dryrun = True if environment == "dev" else False
            tfr, afr = pms.cleanKeyMap(dryrun=dryrun)
            kmsg = "key" if afr == 1 else "keys"
            kmsg += " would be" if environment == "dev" else ""
            msg = "chaim cleanup v{}: {}/{} {} cleaned.".format(version, afr, tfr, kmsg)
            log.info(msg)
            incMetric("cleanup")
            ggMetric("cleanup.cleaned", afr)
            ggMetric("cleanup.existing", tfr)
        else:
            emsg = "chaim cleanup: secret path not in environment"
            log.error(emsg)
            incMetric("cleanup.error")
    except Exception as e:
        emsg = "chaim cleanup v{}: error: {}: {}".format(version, type(e).__name__, e)
        log.error(emsg)
        incMetric("cleanup.error")


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
    getWFKey(stage=environment)
    doCleanup(event, context, version)
