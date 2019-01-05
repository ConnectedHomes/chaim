#
# Copyright (c) 2018, Centrica Hive Ltd.
#
#     This file is part of chaim.
#
#     chaim is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     chaim is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with chaim.  If not, see <http://www.gnu.org/licenses/>.
#
import pytest
from chalicelib.iamclient import IamClient
from chalicelib.botosession import NoCreds


def test_nocreds():
    with pytest.raises(NoCreds):
        IamClient("sre.chaim", accesskey=7)


def test_obtain_access_key_info():
    res = False
    try:
        client = IamClient("sre.chaim")
        user = client.getKeys()
        if type(user) is dict:
            if "keys" in user:
                res = True
            else:
                print(user)
        else:
            print(user)
    except Exception as e:
        print("error: {}: {}".format(type(e).__name__, e))
    assert res is True
