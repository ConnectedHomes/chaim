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
lambda code to rotate the long-term keys for the chaim application
see: https://jira.bgchtest.info/browse/SRE-589
"""

import chalicelib.glue as glue
from chalicelib.envparams import EnvParam
from chalicelib.iamclient import AccessKeyError
from chalicelib.iamclient import IamClient
from chalicelib.paramstore import ParamStore


log = glue.log


def rotate(event, context):
    try:
        ep = EnvParam()
        env = ep.getParam("environment")
        if env in ["dev", "test"]:
            glue.setDebug()
        enckeyname = ep.getParam("KEYNAME")
        iamusername = ep.getParam("CHAIMUSER")
        log.info("Rotating access key for {}".format(iamusername))
        log.debug("enckeyname: {}".format(enckeyname))
        log.debug("iamusername: {}".format(iamusername))
        iam = IamClient(iamusername)
        user = iam.getKeys()
        if user is False:
            log.debug("getkeys is false, yet: {}".format(iam.user["keys"]))
        key = iam.rotateKeys()
        if isinstance(key, dict) and "AccessKey" in key:
            log.debug("new key: {}".format(key))
            accesskeyid = key["AccessKey"]["AccessKeyId"]
            secretkeyid = key["AccessKey"]["SecretAccessKey"]
            ps = ParamStore(usedefault=True)
            ret = ps.putEStringParam("/sre/chaim/accesskeyid", accesskeyid, "alias/" + enckeyname)
            if ret is None:
                raise AccessKeyError("Failed to store encrypted parameter 'accesskeyid'")
            log.debug("storing key ret: {}".format(ret))
            ret = ps.putEStringParam("/sre/chaim/secretkeyid", secretkeyid, "alias/" + enckeyname)
            if ret is None:
                raise AccessKeyError("Failed to store encrypted parameter 'secretkeyid'")
            log.debug("storing secret ret: {}".format(ret))
            log.info("access key rotated for {}".format(iamusername))
        else:
            emsg = "Rotate failed to generate a new key: {}".format(key)
            raise(AccessKeyError(emsg))
    except Exception as e:
        log.error("rotate: {}: {}".format(type(e).__name__, e))
