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
from chaimlib.paramstore import ParamStore


def test_list_parameters():
    ps = ParamStore(usedefault=True)
    devs = ps.listParameters("/sre/chaim/dev")
    assert '/sre/chaim/dev/dbrouser' in devs


def test_getParams():
    plist = ["dbrwuser", "dbrouser"]
    ps = ParamStore(usedefault=True)
    params = ps.getParams(plist)
    assert len(params) == 2 and params["dbrouser"] == "chaimro"


def test_putParam():
    ps = ParamStore(usedefault=True)
    versd = ps.putStringParam("/sre/chaim-test/tester", "A test value")
    vers = int(versd["Version"])
    assert vers > 1


def test_getParam():
    ps = ParamStore(usedefault=True)
    val = ps.getString("/sre/chaim-test/tester")
    assert val == "A test value"
