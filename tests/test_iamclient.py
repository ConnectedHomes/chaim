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
        user = client.getUser()
        if type(user) is dict:
            if "keys" in user:
                res = True
    except Exception as e:
        pass
    assert res == True
