from chaimlib.utils import Utils


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
