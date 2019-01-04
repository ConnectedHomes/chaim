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
"""AWS STS client functions"""

import chaimlib.glue as glue
from chaimlib.botosession import BotoSession

log = glue.log


class StsClient(BotoSession):
    def __init__(self, **kwargs):
        """
        keyword arguments (additional to BotoSession):
            duration - session duration in seconds (default: 3600)
            sessionname - default 'ARSession'
        """
        super().__init__(**kwargs)
        self.sessionname = kwargs["sessionname"] if "sessionname" in kwargs else "ARSession"
        self.duration = kwargs["duration"] if "duration" in kwargs else 3600
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
