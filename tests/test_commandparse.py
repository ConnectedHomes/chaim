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
from chalicelib.commandparse import CommandParse
from chalicelib.commandparse import BadCommandStr
from chalicelib.permissions import Permissions

secretpath = "/sre/chaim/"
stagepath = "dev/"
testbody = "user_name=chris.allison&token=ABCDEF&response_url=http://example.com"
testbody += "&stage=dev&useragent=chaimtest"
goodbody = testbody + "&text=secadmin-prod,apu,1"
swappedbody = testbody + "&text=secadmin-prod,1,apu"
badbody = testbody + "&text=secadmin-prod,apu,zebedee"
oddrolebody = testbody + "&text=secadmin-prod,hlds,2"
rolescmd = testbody + "&text=-r"
countcmd = testbody + "&text=-c"
initshcmd = testbody + "&text=-i"
vercmd = testbody + "&text=-v"
helpcmd = testbody + "&text=-h"
listcmd = testbody + "&text=-l"


def test_cp_init():
    cp = CommandParse("", blankbody=True)
    assert cp.docommand is False


def test_good_request():
    cp = CommandParse(goodbody)
    rd = cp.requestDict()
    assert rd["duration"] == 3600


def test_bad_request():
    with pytest.raises(BadCommandStr):
        CommandParse(badbody)


def test_swap_request():
    cp = CommandParse(swappedbody)
    rd = cp.requestDict()
    assert rd["duration"] == 3600


def test_odd_role_request():
    pms = Permissions(secretpath=secretpath, testdb=True, stagepath=stagepath)
    roledict = pms.roleAliasDict()
    cp = CommandParse(oddrolebody, roledict)
    rd = cp.requestDict()
    assert rd["role"] == "ChaimLeakDataScienceUser"


def test_roles_cmd():
    cp = CommandParse(rolescmd)
    assert (cp.docommand is True) and (cp.doshowroles is True)


def test_count_cmd():
    cp = CommandParse(countcmd)
    assert (cp.docommand is True) and (cp.docountusers is True)


def test_initsh_cmd():
    cp = CommandParse(initshcmd)
    assert (cp.docommand is True) and (cp.doinitshow is True)


def test_ver_cmd():
    cp = CommandParse(vercmd)
    assert (cp.docommand is True) and (cp.doversion is True)


def test_help_cmd():
    cp = CommandParse(helpcmd)
    assert (cp.docommand is True) and (cp.dohelp is True)


def test_list_cmd():
    cp = CommandParse(listcmd)
    assert (cp.docommand is True) and (cp.dolist is True)
