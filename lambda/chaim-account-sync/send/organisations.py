"""AWS Organisations Client"""

import ccalogging

from ccaaws.botosession import BotoSession

log = ccalogging.log


class Organisations(BotoSession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.newClient("organizations")
        self.errored = False
        self.exception = None
        self.accounts = []

    def retrieveAccounts(self):
        """Retrieves a list of accounts from AWS and stores them in self.accounts.

        As the accounts list from AWS is sent as a series of pages, this function
        will iterate over the pages until no more data is available.
        On error, self.errored is set True and the exception is logged and
        stored in self.exception.
        """
        nextpage = ""
        pages = 0
        log.debug("Retrieving accounts...")
        while pages == 0 or len(nextpage):
            try:
                if len(nextpage):
                    resp = self.client.list_accounts(NextToken=nextpage)
                    log.debug("paging: {}".format(resp))
                else:
                    resp = self.client.list_accounts()
                    log.debug("1st. page: {}".format(resp))
            except Exception as E:
                log.error(
                    "Failed to retrieve account information, Exception: {}".format(E)
                )
                self.errored = True
                self.exception = E
                break
            if "NextToken" in resp:
                nextpage = resp["NextToken"]
            else:
                nextpage = ""
            pages += 1
            log.debug("appending page {} to list of accounts".format(pages))
            log.debug("retrieved {} accounts so far".format(len(self.accounts)))
            for acct in resp["Accounts"]:
                self.accounts.append(acct)
        log.debug(
            "Retrieved {} accounts in {} pages.".format(len(self.accounts), pages)
        )

    def getAccounts(self):
        if len(self.accounts) == 0:
            self.retrieveAccounts()
        return self.accounts

    def accountIdsList(self):
        idslist = None
        if len(self.accounts) == 0:
            self.retrieveAccounts()
        if not self.errored:
            idslist = []
            for acct in self.accounts:
                if acct["Status"] == "ACTIVE":
                    idslist.append(acct["Id"])
        return idslist

    def accountIdsString(self, seperator=","):
        xstr = False
        idslist = self.accountIdsList()
        if idslist is not None:
            for xid in idslist:
                if False == xstr:
                    xstr = "{}".format(xid)
                else:
                    xstr = "{}{}{}".format(xstr, seperator, xid)
        return xstr
