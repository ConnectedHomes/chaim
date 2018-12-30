import os
import chaimlib.glue as glue
from chaimlib.envparams import EnvParam
from chaimlib.wflambda import getWFKey

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
