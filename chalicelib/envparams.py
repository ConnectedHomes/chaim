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
"""Environment Parameters (via KMS) module"""

import os
import chardet
from chalicelib.kmsclient import KmsClient
import chalicelib.glue as glue

log = glue.log


class EnvParam():
    def getParam(self, param, decode=False):
        xstr = False
        try:
            tstr = os.environ[param]
            if decode:
                xstr = self.decodeStr(tstr)
            else:
                xstr = tstr
        except Exception as e:
            log.warning("Error when retrieving environment parameter {}, exception was {}".format(param, e))  # nopep8
        return xstr

    def getEncParam(self, param):
        xparam = False
        eparam = self.getParam(param, False)
        if eparam is not False:
            kmsc = KmsClient(defaultsession=True)
            dparam = kmsc.decrypt(eparam)
            if dparam is not False:
                xparam = self.decodeStr(dparam)
        return xparam

    def decodeStr(self, data):
        # this function is necessary in python3 as strings coming
        # from the environment and boto3 CAN be a stream of bytes
        # which breaks later usage
        # returns decoded data, or leaves data unchanged.
        if isinstance(data, bytes):
            # use chardet to detect encoding
            dect = chardet.detect(data)
            log.debug("data bytes string {} encoded as {} with confidence of {}".format(data, dect["encoding"], dect["confidence"]))  # nopep8
            res = data.decode(dect["encoding"])
        else:
            res = data
        return res
