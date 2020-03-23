import boto3

import ccalogging

import organisations as ORG

ccalogging.setConsoleOut()
ccalogging.setInfo()
log = ccalogging.log

majorv = 1
minorv = 0
buildv = 0
verstr = str(majorv) + "." + str(minorv) + "." + str(buildv)
__version__ = verstr
__version_info__ = [majorv, minorv, buildv]


def send(event, context, local=False):
    try:
        log.info(f"Chaim Account Sync Send version: {__version__}")
        org = ORG.Organisations()
        accts = org.getAccounts()
        acn = 0
        icn = 0
        iaccts = []
        if local:
            for acct in accts:
                if acct["Status"] == "ACTIVE":
                    acn += 1
                else:
                    icn += 1
                    iaccts.append(acct)
            log.info(f"{acn} active accounts")
            log.info(f"{icn} inactive accounts")
            log.info(iaccts)
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
