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
