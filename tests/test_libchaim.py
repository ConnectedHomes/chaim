import os
import chaimlib.chaim as chaim

os.environ["REPORT_STANDARD_METRICS"] = "True"
os.environ["SECRETPATH"] = "/sre/chaim"
os.environ["WAVEFRONT_URL"] = "https://connectedhome.wavefront.com"


testbody = "user_name=chris.allison&token=ABCDEF&response_url=http://example.com"
goodbody = testbody + "&text=secadmin-prod,apu,1"
testextra = "&stage=dev&useragent=chaimtest"


def test_begin():
    b = chaim.begin(testbody, {}, False)
    assert len(b) != len(testbody)
