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
from chaimlib.stsclient import StsClient
from chaimlib.assumedrole import AssumedRole


def test_stsclient():
    sts = StsClient()
    assert sts.client is not None


def test_sts_assumeRole():
    ret = False
    sts = StsClient()
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro = sts.assumeRole(arn)
    if "Credentials" in aro:
        if "AccessKeyId" in aro["Credentials"]:
            ret = True
    assert ret is True


def test_sts_assumeRoleStr():
    sts = StsClient()
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro, x = sts.assumeRoleStr(arn)
    y = x[0:33]
    lx = len(x)
    assert (lx >= 500) and (y == "```\nexport AWS_ACCESS_KEY_ID=ASIA")


def test_assumedRole_self():
    sts = StsClient()
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro = sts.assumeRole(arn)
    ar = AssumedRole(aro)
    assert ar.ok is True


def test_assumedRole_getCreds():
    sts = StsClient()
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro = sts.assumeRole(arn)
    ar = AssumedRole(aro)
    creds = ar.getCreds()
    ret = False
    if "sessionId" in creds:
        ret = True
    assert ret is True
