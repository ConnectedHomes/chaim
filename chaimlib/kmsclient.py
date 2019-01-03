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
"""AWS KMS client functions"""

from chaimlib.botosession import BotoSession
from base64 import b64decode
import chaimlib.glue as glue

log = glue.log


class KmsClient(BotoSession):
    def __init__(self, awsaccessid=None, awssecretkey=None, awsprofile=None, defaultsession=True, stoken=None):
        super().__init__(accessid=awsaccessid, secretkey=awssecretkey, theprofile=awsprofile,
                         usedefault=defaultsession, stoken=stoken)
        self.newClient('kms')

    def decrypt(self, encstr):
        dstr = False
        try:
            dstr = self.client.decrypt(CiphertextBlob=b64decode(encstr))['Plaintext']
        except Exception as e:
            log.warning("Failed to decrypt encoded value. Exception was: {}".format(e))
        return dstr
