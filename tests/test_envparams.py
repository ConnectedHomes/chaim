import os
from chaimlib.envparams import EnvParam

os.environ["TESTPARAM"] = "ATESTPARAM"


def test_param_not_exist():
    ep = EnvParam()
    val = ep.getParam("NOTEXIST")
    assert val is False


def test_param_exist():
    ep = EnvParam()
    value = ep.getParam("TESTPARAM")
    assert value == "ATESTPARAM"
