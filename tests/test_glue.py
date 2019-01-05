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
import chalicelib.glue as glue
from chalicelib.envparams import EnvParam
from chalicelib.wflambda import getWFKey

os.environ["SECRETPATH"] = "/sre/chaim/"
os.environ["WAVEFRONT_URL"] = "https://connectedhome.wavefront.com"
os.environ["REPORT_STANDARD_METRICS"] = "False"


def test_getDefaultValue_exists():
    xdict = {"one": 1, "two": 2, "three": "3"}
    val = glue.getDefaultValue(xdict, "two", 4)
    assert val == 2


def test_getDefaultValue_notexists():
    xdict = {"one": 1, "two": 2, "three": "3"}
    val = glue.getDefaultValue(xdict, "four", 4)
    assert val == 4


def test_addToReqBody_exists():
    rbd = "query=hello&string=world"
    nbd = glue.addToReqBody(rbd, "new", "new")
    assert nbd == rbd + "&new=new"


def test_addToReqBody_notexists():
    nbd = glue.addToReqBody("", "new", "new")
    assert nbd == "new=new"


def test_getWFKey():
    getWFKey("dev")
    ep = EnvParam()
    wft = ep.getParam("WAVEFRONT_API_TOKEN", True)
    assert wft is not False


def test_loglevelwarn():
    lvl = glue.log.getEffectiveLevel()
    assert lvl is 30


def test_logleveldebug():
    lvl = glue.log.getEffectiveLevel()
    glue.setDebug()
    assert (lvl is 30) and (10 is glue.log.getEffectiveLevel())


def test_addToOutStr_empty():
    xstr = glue.addToOutStr("", "", "")
    assert xstr == "\n = \n"


def test_addToOutStr_empty_init():
    xstr = glue.addToOutStr("", "new", "new")
    assert xstr == "\nnew = new\n"


def test_addToOutStr():
    xstr = "eric = two"
    xstr = glue.addToOutStr(xstr, "new", "unnew")
    assert xstr == "eric = two\nnew = unnew\n"
