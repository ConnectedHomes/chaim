import pytest
from chaimlib.iamclient import IamClient
from chaimlib.botosession import NoCreds

def test_nocreds():
    with pytest.raises(NoCreds):
        client = IamClient()

def test_obtain_access_key_info():
    res = False
    try:
        client = IamClient(defaultsession=True)
        user = client.getKeys("sre.chaim")
        if type(user) is dict:
            if "keys" in user:
                res = True
            else:
                print(user)
        else:
            print(user)
    except Exception as e:
        print("error: {}: {}".format(type(e).__name__, e))
    assert res == True
