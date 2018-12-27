import pytest
import os
from chaimlib.envparams import EnvParam

os.environ["TESTPARAM"] = "ATESTPARAM"


def test_param_not_exist():
    with pytest.raises(Exception):
        ep = EnvParam()
        ep.getParam("NOTEXIST")


def test_param_exist():
    ep = EnvParam()
    value = ep.getParam("TESTPARAM")
    assert value == "ATESTPARAM"
