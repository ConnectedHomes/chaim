import os
import chaimlib.chaim as chaim
from chaimlib.permissions import Permissions
from chaimlib.commandparse import CommandParse

os.environ["REPORT_STANDARD_METRICS"] = "True"
os.environ["SECRETPATH"] = "/sre/chaim"
os.environ["WAVEFRONT_URL"] = "https://connectedhome.wavefront.com"


testbody = "user_name=chris.allison&token=" + os.environ["UTOK"] + "&response_url=http://example.com"
goodbody = testbody + "&text=secadmin-prod,apu,1"
testextra = "&text=-i"
context = {"useragent": "chaimtest", "stage": "dev", "apiId": "testapi"}


def test_begin():
    b = chaim.begin(testbody, context, False)
    assert len(b) != len(testbody)


def test_bodyparams():
    d = chaim.bodyParams(testbody)
    assert d["user_name"] == "chris.allison"


def test_begin_fully():
    tb = chaim.bodyParams(testbody)
    td = chaim.bodyParams(chaim.begin(testbody, context, isSlack=True))
    assert ("useragent" not in tb) and (td["useragent"] == "slack")


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
    b = chaim.begin(testbody + testextra, context, False)
    pms = Permissions(os.environ["SECRETPATH"], True)
    cp = CommandParse(b, pms.roleAliasDict())
    xs = chaim.readKeyInit(cp.requestDict(), pms)
    assert xs[0:24] == "Chaim Credentials Expire"
