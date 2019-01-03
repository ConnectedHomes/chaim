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
from chaimlib.botosession import NoCreds
from chaimlib.cognitoclient import CognitoClient

chaimpoolid = "eu-west-1_o9gzAnQkS"
chaimuserfind = "chris.allison"
chaimuseremail = "chris.allison@hivehome.com"
chaimminnumusers = 100


def test_nocreds():
    with pytest.raises(NoCreds):
        CognitoClient(defaultsession=False)


def test_has_pools():
    cc = CognitoClient()
    pools = cc.listPools()
    cn = len(pools)
    assert cn > 0


def test_pool_list():
    cc = CognitoClient()
    pools = cc.listPools()
    pool = pools[0]
    assert "Id" in pool


def test_correct_pool_list():
    cc = CognitoClient()
    pools = cc.listPools()
    pool = pools[0]
    assert pool["Id"] == chaimpoolid


def test_has_min_num_users():
    cc = CognitoClient()
    users = cc.listUsers(chaimpoolid)
    cn = len(users)
    assert cn >= chaimminnumusers


def test_find_user():
    cc = CognitoClient()
    users = cc.listUsers(chaimpoolid)
    found = False
    for user in users:
        if user["Username"] == chaimuserfind:
            found = True
            break
    assert found is True


def test_admin_get_user():
    cc = CognitoClient()
    user = cc.adminGetUser(chaimpoolid, chaimuserfind)
    assert user["Username"] == chaimuserfind


def test_find_by_email_address():
    cc = CognitoClient()
    user = cc.findUserByEmail(chaimpoolid, chaimuseremail)
    assert user["Username"] == chaimuserfind


def test_find_by_email_name():
    cc = CognitoClient()
    user = cc.findUserByEmail(chaimpoolid, chaimuserfind)
    assert user["Username"] == chaimuserfind
