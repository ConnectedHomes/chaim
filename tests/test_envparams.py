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
import os
from chalicelib.envparams import EnvParam

os.environ["TESTPARAM"] = "ATESTPARAM"


def test_param_not_exist():
    ep = EnvParam()
    val = ep.getParam("NOTEXIST")
    assert val is False


def test_param_exist():
    ep = EnvParam()
    value = ep.getParam("TESTPARAM")
    assert value == "ATESTPARAM"
