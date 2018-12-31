from chaimlib.stsclient import StsClient
from chaimlib.assumedrole import AssumedRole


def test_stsclient():
    sts = StsClient(usedefault=True)
    assert sts.client is not None


def test_sts_assumeRole():
    ret = False
    sts = StsClient(usedefault=True)
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro = sts.assumeRole(arn)
    if "Credentials" in aro:
        if "AccessKeyId" in aro["Credentials"]:
            ret = True
    assert ret is True


def test_sts_assumeRoleStr():
    sts = StsClient(usedefault=True)
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro, x = sts.assumeRoleStr(arn)
    y = x[0:33]
    lx = len(x)
    assert (lx == 513) and (y == "```\nexport AWS_ACCESS_KEY_ID=ASIA")


def test_assumedRole_self():
    sts = StsClient(usedefault=True)
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro = sts.assumeRole(arn)
    ar = AssumedRole(aro)
    assert ar.ok is True


def test_assumedRole_getCreds():
    sts = StsClient(usedefault=True)
    arn = "arn:aws:iam::499223386158:role/CrossAccountReadOnly"
    aro = sts.assumeRole(arn)
    ar = AssumedRole(aro)
    creds = ar.getCreds()
    ret = False
    if "sessionId" in creds:
        ret = True
    assert ret is True
