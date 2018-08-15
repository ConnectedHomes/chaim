"""Environment Parameters (via KMS) module"""

import os
import chardet
from kmsclient import KmsClient
import logging

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


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
