import organisations as ORG


def send(event, context, local=False):
    org = ORG.Organisations(noresource=True)
    accts = org.getAccounts()
    acn = 0
    icn = 0
    iaccts = []
    for acct in accts:
        if acct["Status"] == "ACTIVE":
            acn += 1
        else:
            icn += 1
            iaccts.append(acct)
    print(f"{acn} active accounts")
    print(f"{icn} inactive accounts")
    print(iaccts)


if __name__ == "__main__":
    send(None, None, True)
