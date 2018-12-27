import os
import chaimlib.chaim as chaim
from chaimlib.envparams import EnvParam

os.environ["SECRETPATH"] = "/sre/chaim/"
os.environ["WAVEFRONT_URL"] = "https://connectedhome.wavefront.com"
os.environ["REPORT_STANDARD_METRICS"] = "False"


def test_getDefaultValue_exists():
    xdict = {"one": 1, "two": 2, "three": "3"}
    val = chaim.getDefaultValue(xdict, "two", 4)
    assert val == 2


def test_getDefaultValue_notexists():
    xdict = {"one": 1, "two": 2, "three": "3"}
    val = chaim.getDefaultValue(xdict, "four", 4)
    assert val == 4


def test_addToReqBody_exists():
    rbd = "query=hello&string=world"
    nbd = chaim.addToReqBody(rbd, "new", "new")
    assert nbd == rbd + "&new=new"


def test_addToReqBody_notexists():
    nbd = chaim.addToReqBody("", "new", "new")
    assert nbd == "new=new"


def test_getWFKey():
    chaim.getWFKey("dev")
    ep = EnvParam()
    wft = ep.getParam("WAVEFRONT_API_TOKEN", True)
    assert wft is not False
