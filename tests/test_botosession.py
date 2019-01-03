import pytest
from chaimlib.botosession import BotoSession
from chaimlib.botosession import NoCreds


def test_nocreds():
    with pytest.raises(NoCreds):
        BotoSession()


def test_default_creds():
    sess = BotoSession(usedefault=True)
    assert sess.usedefault
