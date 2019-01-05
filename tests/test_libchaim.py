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
import chalicelib.chaim as chaim
from chalicelib.permissions import Permissions
from chalicelib.commandparse import CommandParse

os.environ["REPORT_STANDARD_METRICS"] = "True"
os.environ["SECRETPATH"] = "/sre/chaim"
os.environ["WAVEFRONT_URL"] = "https://connectedhome.wavefront.com"


testbody = "user_name=chris.allison&token=" + os.environ["UTOK"] + "&response_url=http://example.com"
goodbody = testbody + "&text=secadmin-prod,apu,1"
testextra = "&text=-i"
context = {"useragent": "chaimtest", "environment": "dev", "apiid": "testapi"}
contextbody = testbody + "&stage=dev&apiid=testapi&useragent=chaimtest"


def test_begin():
    b = chaim.begin(testbody, **context)
    assert b == contextbody


def test_bodyparams():
    d = chaim.bodyParams(testbody)
    assert d["user_name"] == "chris.allison"


def test_begin_fully():
    tb = chaim.bodyParams(testbody)
    td = chaim.bodyParams(chaim.begin(testbody, **context))
    assert ("useragent" not in tb) and (td["useragent"] == "chaimtest")


def test_makeattachments():
    att = "this is the attachment"
    title = "this is the title"
    xl = chaim.makeAttachments(att, title)
    expl = [{"title": title, "title_link": att, "mrkdwn_in": ["text", "pretext"]}]
    assert xl == expl


def test_output():
    err = None
    out = "some message"
    att = "This is attached"
    title = None
    xd = chaim.output(err, out, att)
    ed = {'response_type': 'ephemeral', 'statusCode': '200', 'text': 'some message'}
    ed["headers"] = {'Content-Type': 'application/json'}
    ed["attachments"] = [{"title": title, "title_link": att, "mrkdwn_in": ["text", "pretext"]}]
    assert xd == ed


def test_readKeyInit():
    b = chaim.begin(testbody + testextra, **context)
    pms = Permissions(os.environ["SECRETPATH"], True)
    cp = CommandParse(b, pms.roleAliasDict())
    xs = chaim.readKeyInit(cp.requestDict(), pms)
    assert xs[0:24] == "Chaim Credentials Expire"
