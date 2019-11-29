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
import time
from chaim.chaimmodule import Chaim

def test_chaim_contextmanager():
    with Chaim("sredev", "rro", verbose=0) as success:
        assert success == True

def test_chaim_ctx_fail():
    with Chaim("Connected Homes", "rro", verbose=0) as success:
        assert success == False

def test_allAccountList():
    ch = Chaim("sredev", "rro")
    lst = ch.requestList()
    found = False
    for acct in lst:
        if acct[0] == "324919260230" and acct[1] == "Connected Homes":
            found = True
            break
    assert found == True

def test_myAccountList():
    ch = Chaim("sredev", "rro")
    lst = ch.myAccountList()
    now = int(time.time())
    if len(lst) > 1:
        ts = int(lst[0][1])
        assert ts > now
    else:
        assert False == True

def findInList(item, lst):
    found = False
    for acct in lst:
        if acct == item:
            found = True
            break
    return found

def test_listParked():
    ch = Chaim("sredev", "rro")
    lst = ch.listParkAccounts()
    found = findInList("hprod", lst)
    assert found == True

def test_parking():
    ch = Chaim("sredev", "rro", verbose=0)
    ch.unparkAccount("hprod")
    lst = ch.listParkAccounts()
    found = findInList("hprod", lst)
    if not found:
        ch.parkAccount("hprod")
        lst = ch.listParkAccounts()
        found = findInList("hprod", lst)
        assert found == True
    else:
        assert found == False
