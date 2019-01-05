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
from chalicelib.utils import Utils


ut = Utils()


def test_isNumeric_int():
    b = ut.isNumeric(7)
    assert b is True


def test_isNumeric_str():
    b = ut.isNumeric("7")
    assert b is True


def test_isNumeric_alpha_str():
    b = ut.isNumeric("A")
    assert b is False


def test_valMod():
    val, rem = ut.valMod(17, 2)
    assert (val == 8) and (rem == 1)


def test_hms():
    hrs, mins, secs = ut.hms(3600 + (12*60) + 32)
    assert (hrs == 1) and (mins == 12) and (secs == 32)


def test_dhms():
    ds, hrs, mins, secs = ut.dhms(3600 + (12*60) + 32)
    assert (ds == 0) and (hrs == 1) and (mins == 12) and (secs == 32)


def test_displayWord_single():
    x = ut.displayWord(1, "block")
    assert x == "1 block"


def test_displayWord_plural():
    x = ut.displayWord(3, "block")
    assert x == "3 blocks"


def test_hmsDisplay_short():
    x = ut.hmsDisplay(86821)
    assert x == "1 day, 0 hours, 7 minutes and 1 second"

def test_expiresAt():
    x = ut.expiresAt(1546345853)
    assert x == "Tue Jan  1 12:30:53 2019"
