import pytest
from chaimlib.botosession import NoCreds
from chaimlib.cognitoclient import CognitoClient

chaimpoolid = "eu-west-1_o9gzAnQkS"
chaimuserfind = "chris.allison"
chaimuseremail = "chris.allison@hivehome.com"
chaimminnumusers = 100


def test_nocreds():
    with pytest.raises(NoCreds):
        CognitoClient(defaultsession=False)


def test_has_pools():
    cc = CognitoClient()
    pools = cc.listPools()
    cn = len(pools)
    assert cn > 0


def test_pool_list():
    cc = CognitoClient()
    pools = cc.listPools()
    pool = pools[0]
    assert "Id" in pool


def test_correct_pool_list():
    cc = CognitoClient()
    pools = cc.listPools()
    pool = pools[0]
    assert pool["Id"] == chaimpoolid


def test_has_min_num_users():
    cc = CognitoClient()
    users = cc.listUsers(chaimpoolid)
    cn = len(users)
    assert cn >= chaimminnumusers


def test_find_user():
    cc = CognitoClient()
    users = cc.listUsers(chaimpoolid)
    found = False
    for user in users:
        if user["Username"] == chaimuserfind:
            found = True
            break
    assert found is True


def test_admin_get_user():
    cc = CognitoClient()
    user = cc.adminGetUser(chaimpoolid, chaimuserfind)
    assert user["Username"] == chaimuserfind


def test_find_by_email_address():
    cc = CognitoClient()
    user = cc.findUserByEmail(chaimpoolid, chaimuseremail)
    assert user["Username"] == chaimuserfind


def test_find_by_email_name():
    cc = CognitoClient()
    user = cc.findUserByEmail(chaimpoolid, chaimuserfind)
    assert user["Username"] == chaimuserfind
