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

import chaimlib.glue as glue
from chaimlib.botosession import BotoSession
from chaimlib.botosession import NoCreds
from chaimlib.paramstore import ParamStore


log = glue.log


def rotate(event, context):
    try:
        ps = ParamStore(usedefault=True)
        enckeyname = ps.getEString("/sre/chaim/encryptionkey")
        log.debug("enckeyname: {}".format(enckeyname))
        iamusername = ps.getEString("/sre/chaim/iamusername")
        log.info("Rotating access key for {}".format(iamusername))
        log.debug("iamusername: {}".format(iamusername))
        iam = IamClient(defaultsession=True)
        user = iam.getKeys(username=iamusername)
        if user is False:
            log.debug("getkeys is false, yet: {}".format(iam.user["keys"]))
        key = iam.rotateKeys()
        log.debug("new key: {}".format(key))
        accesskeyid = key["AccessKey"]["AccessKeyId"]
        secretkeyid = key["AccessKey"]["SecretAccessKey"]
        ret = ps.putEStringParam("/sre/chaim/accesskeyid", accesskeyid, "alias/" + enckeyname)
        if ret is None:
            raise AccessKeyError("Failed to store encrypted parameter 'accesskeyid'")
        log.debug("storing key ret: {}".format(ret))
        ret = ps.putEStringParam("/sre/chaim/secretkeyid", secretkeyid, "alias/" + enckeyname)
        if ret is None:
            raise AccessKeyError("Failed to store encrypted parameter 'secretkeyid'")
        log.debug("storing secret ret: {}".format(ret))
        log.info("access key rotated for {}".format(iamusername))
    except Exception as e:
        log.error("exception {}".format(e))
