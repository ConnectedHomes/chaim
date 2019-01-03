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
from chaimlib.permissions import Permissions
from chaimlib.permissions import DataNotFound
from chaimlib.permissions import IncorrectCredentials

secretpath = "/sre/chaim/"
stagepath = "dev/"


def test_perms_bad_creds():
    with pytest.raises(IncorrectCredentials):
        Permissions(secretpath=secretpath, stagepath="Incorrect")


def test_perms_good_creds():
    pms = Permissions(secretpath=secretpath, stagepath=stagepath, quick=True, missing=True)
    assert pms.params["dbrouser"] == "chaimro"


def test_db_not_connected():
    with pytest.raises(Exception):
        pms = Permissions(secretpath=secretpath, stagepath=stagepath, testdb=False)
        pms.userAllowed("chris.allison", "secadmin-prod", "apu")


def test_bad_user():
    with pytest.raises(DataNotFound):
        pms = Permissions(secretpath=secretpath, testdb=True, stagepath=stagepath)
        pms.userAllowed("a.bad.test.user", "a.bad.account", "abadrole")


def test_good_user():
    with pytest.raises(DataNotFound):
        pms = Permissions(secretpath=secretpath, testdb=True, stagepath=stagepath)
        pms.userAllowed("chris.allison", "secadmin-prod", "mpu")
