"""AWS STS client functions"""

import chaimlib.glue as glue
from chaimlib.botosession import BotoSession

log = glue.log


class StsClient(BotoSession):
    def __init__(self, awsaccessid=None, awssecretkey=None,
                 awsprofile=None, usedefault=False, stoken=None,
                 sessionname="ARSession", duration=3600):
        super().__init__(accessid=awsaccessid, secretkey=awssecretkey,
                         theprofile=awsprofile, usedefault=usedefault,
                         stoken=stoken)
        self.sessionname = sessionname
        self.duration = duration
        self.newClient('sts')

    def assumeRole(self, rolearn):
        assumedRole = None
        try:
            assumedRole = self.client.assume_role(RoleArn=rolearn, RoleSessionName=self.sessionname,
                                                  DurationSeconds=self.duration)
            log.debug("Assumed role for arn: {}: {}".format(rolearn, assumedRole))  # nopep8
        except Exception as e:
            log.error("Failed to assume role. Exception: {}".format(e))
        return assumedRole

    def assumeRoleStr(self, rolearn):
        xstr = ""
        aro = self.assumeRole(rolearn)
        if aro is not None:
            xstr = self.buildOutStr(aro)
        return [aro, xstr]

    def buildOutStr(self, aro):
        delim = "```"
        lines = [delim]
        tstr = "export AWS_ACCESS_KEY_ID="
        tstr += aro["Credentials"]["AccessKeyId"]
        lines.append(tstr)
        tstr = "export AWS_SECRET_ACCESS_KEY="
        tstr += aro["Credentials"]["SecretAccessKey"]
        lines.append(tstr)
        tstr = "export AWS_SESSION_TOKEN="
        tstr += aro["Credentials"]["SessionToken"]
        lines.append(tstr)
        lines.append(delim)
        return "\n".join(lines)
