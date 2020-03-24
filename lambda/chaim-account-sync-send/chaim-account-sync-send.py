import boto3
import json
import os

import ccalogging

import organisations as ORG

ccalogging.setConsoleOut()
ccalogging.setInfo()
log = ccalogging.log

majorv = 1
minorv = 1
buildv = 2
verstr = str(majorv) + "." + str(minorv) + "." + str(buildv)
__version__ = verstr
__version_info__ = [majorv, minorv, buildv]


def makeAcct(oacct):
    keys = ["Id", "Name"]
    acct = {}
    for key in keys:
        acct[key] = oacct[key]
    return acct


def makeAccts(oaccts):
    accts = []
    inactive = []
    for oa in oaccts:
        if oa["Status"] == "ACTIVE":
            accts.append(makeAcct(oa))
        else:
            inactive.append(makeAcct(oa))
    return (inactive, accts)


def send(event, context, local=False):
    try:
        log.info(f"Chaim Account Sync Send version: {__version__}")
        org = ORG.Organisations()
        inactive, accts = makeAccts(org.getAccounts())
        log.info(f"{len(accts)} accounts retrieved")
        log.info(f"{len(inactive)} inactive accounts")
        log.debug(f"Accounts: {accts}")
        if local:
            jop = json.dumps(accts)
            ccalogging.setDebug()
            log.debug(inactive)
        else:
            jop = json.dumps(accts)
            topic = os.environ.get("SNSTOPIC", None)
            if topic is not None:
                sns = boto3.client("sns")
                resp = sns.publish(TopicArn=topic, Message=jop)
                if "MessageId" in resp:
                    log.info(f"""Published to SNS: {resp["MessageId"]} ({topic})""")
                else:
                    log.error("Failed to publish to SNS {topic}")
    except Exception as e:
        log.error(f"Exception: {e}")


if __name__ == "__main__":
    send(None, None, True)
