import pytest
from chaimlib.permissions import Permissions
from chaimlib.permissions import DataNotFound
from chaimlib.permissions import IncorrectCredentials

secretpath = "/sre/chaim/"
stagepath = "dev/"


def test_perms_bad_creds():
    with pytest.raises(IncorrectCredentials):
        Permissions(secretpath=secretpath, stagepath="Incorrect")


def test_perms_good_creds():
    pms = Permissions(secretpath=secretpath, stagepath=stagepath, quick=True, missing=True)
    assert pms.params["dbrouser"] == "chaimro"


def test_db_not_connected():
    with pytest.raises(Exception):
        pms = Permissions(secretpath=secretpath, stagepath=stagepath, testdb=False)
        pms.userAllowed("chris.allison", "secadmin-prod", "apu")


def test_bad_user():
    with pytest.raises(DataNotFound):
        pms = Permissions(secretpath=secretpath, testdb=True, stagepath=stagepath)
        pms.userAllowed("a.bad.test.user", "a.bad.account", "abadrole")


def test_good_user():
    with pytest.raises(DataNotFound):
        pms = Permissions(secretpath=secretpath, testdb=True, stagepath=stagepath)
        pms.userAllowed("chris.allison", "secadmin-prod", "mpu")
