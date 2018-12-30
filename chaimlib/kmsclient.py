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
