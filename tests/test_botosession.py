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
import pytest
from chalicelib.botosession import BotoSession
from chalicelib.botosession import NoCreds


def test_nocreds():
    with pytest.raises(NoCreds):
        kwargs = {"accesskey": 7}
        BotoSession(**kwargs)


def test_default_creds():
    sess = BotoSession()
    assert sess.profile is None


def test_profile():
    ret = False
    kwargs = {"profile": "extbackup"}
    sess = BotoSession(**kwargs)
    cli = sess.newClient("iam")
    usr = cli.get_user(UserName="aws.events.ro")
    if "User" in usr:
        if "Arn" in usr["User"]:
            if usr["User"]["Arn"] == "arn:aws:iam::571376643458:user/aws.events.ro":
                ret = True
    assert ret is True
