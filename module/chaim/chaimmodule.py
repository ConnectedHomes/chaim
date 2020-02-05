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
"""
chaim module for python scripting with chaim

This is the module that does all the work
"""

import ast
import sys
import os
import subprocess
import time
import requests
import json
import base64
import ccalogging
import chaim.utils as utils
from chaim.inifile import IniFile
from chaim.errors import errorRaise
from chaim.errors import errorNotify
from chaim.errors import errorExit
from chaim import __version__ as version

log = ccalogging.log


class UnmanagedAccount(Exception):
    pass


class NoUrl(Exception):
    pass


class Chaim(object):
    def __init__(
        self,
        account,
        role,
        duration=1,
        region="eu-west-1",
        tempname="tempname",
        terrible=False,
        verbose=-1,
        logfile=None,
    ):
        self.verbose = verbose
        if logfile is not None:
            ccalogging.setLogFile(logfile)
        if self.verbose == 0:
            ccalogging.setWarn()
        elif self.verbose == 1:
            ccalogging.setInfo()
        elif self.verbose > 1:
            ccalogging.setDebug()
        self.root = os.path.expanduser("~/.aws")
        self.credsfn = self.root + "/credentials"
        self.parkfn = self.root + "/chaim-parked"
        self.ifn = IniFile(self.credsfn, takebackup=False)
        self.pfn = IniFile(self.parkfn, takebackup=False)
        self.account = account
        self.role = role
        self.duration = duration
        self.region = region
        self.accountalias = tempname
        self.terrible = terrible
        self.holdaccount = None

    def __enter__(self):
        return self.requestKeys()

    def __exit__(self, xtype, value, traceback):
        self.deleteAccount(self.accountalias)
        return True

    def __del__(self):
        self.deleteAccount(self.accountalias)

    def getDefaultSection(self):
        ret = None
        if "default" in self.ifn.titles():
            ret = self.ifn.getSectionItems("default")
        else:
            self.ifn.add_section("default")
            ret = self.ifn.getSectionItems("default")
        return ret

    def getDefaultAccount(self):
        ret = None
        defsect = self.getDefaultSection()
        if "section" in defsect:
            ret = defsect["alias"] if "alias" in defsect else defsect["section"]
        return ret

    def getEndpoint(self):
        defsect = self.getDefaultSection()
        endpoint = "https://{}.".format(defsect["api"])
        endpoint += "execute-api.{}.".format(defsect["region"])
        endpoint += "amazonaws.com/{}/".format(defsect["stage"])
        return endpoint

    def renewSection(self, section):
        """renews the config file section named 'section'"""
        defsect = self.getDefaultSection()
        if section in self.ifn.titles():
            sect = self.ifn.getSectionItems(section)
            if "accountname" in sect:
                if self.account != account:
                    self.holdaccount = self.account
                self.account = sect["accountname"]
                self.duration = sect["duration"]
                self.role = sect["role"]
                self.accountalias = section
                default = False
                if "region" in sect:
                    self.region = sect["region"]
                self.terrible = True if "aws_security_token" in sect else False
                if self.holdaccount is not None:
                    self.account = self.holdaccount
                    self.holdaccount = None
                return self.requestKeys()
            else:
                raise UnmanagedAccount(
                    "ignoring " + section + " as it is not managed by cca"
                )
        else:
            return False

    def requestKeys(self):
        ret = False
        defsect = self.getDefaultSection()
        if self.account == "NOT SET":
            return ret
        if len(self.accountalias) == 0:
            self.accountalias = self.account
        if self.verbose > 0:
            log.info(
                "account: {}, alias: {}, role: {}, duration: {}".format(
                    self.account, self.accountalias, self.role, self.duration
                )
            )
        params = {"text": "{},{},{}".format(self.account, self.role, self.duration)}
        params["user_name"] = defsect["username"]
        params["token"] = defsect["usertoken"]
        params["response_url"] = "ignoreme"
        params["useragent"] = "cca " + version
        if "slackid" in defsect:
            params["user_id"] = defsect["slackid"]
        if "workspaceid" in defsect:
            params["team_id"] = defsect["workspaceid"]
        endpoint = self.getEndpoint()
        # click.echo("params: {}".format(params))
        now = int(time.time())
        r = requests.post(endpoint, data=params)
        taken = int(time.time()) - now
        if 200 == r.status_code:
            d = r.json()
            if isinstance(d, dict):
                if "statusCode" in d:
                    sc = int(d["statusCode"])
                    if sc > 399:
                        log.error("Error: {}: {}".format(sc, d["text"]), exc_info=True)
                    else:
                        ret = self.storeKeys(d["text"])
                        if self.verbose > 0:
                            log.info(
                                "{} retrieval took {} seconds.".format(
                                    self.accountalias, taken
                                )
                            )
            else:
                log.error("d is not a dict", exc_info=True)
        else:
            log.error(
                "status: {} response: {}".format(r.status_code, r.text), exc_info=True
            )
        return ret

    def storeKeys(self, text):
        ret = False
        defsect = self.getDefaultSection()
        xd = json.loads(text.replace("'", '"'))
        if isinstance(xd, dict):
            dd = {}
            dd["aws_access_key_id"] = xd["accesskeyid"]
            dd["aws_secret_access_key"] = xd["secretkey"]
            dd["aws_session_token"] = xd["sessiontoken"]
            if self.terrible:
                dd["aws_security_token"] = xd["sessiontoken"]
            dd["expires"] = str(xd["expires"])
            dd["expstr"] = xd["expiresstr"]
            dd["duration"] = str(self.duration)
            dd["gui_url"] = xd["url"]
            dd["role"] = self.role
            dd["accountname"] = xd["sectionname"]
            dd["region"] = self.region
            if self.accountalias not in self.ifn.titles():
                # log.debug("adding account: {}".format(accountalias))
                self.ifn.add_section(self.accountalias)
            if self.ifn.updateSection(self.accountalias, dd, True):
                if self.verbose > 0:
                    log.info(
                        "Updated section {} with new keys".format(xd["sectionname"])
                    )
                ret = True
            else:
                log.error(
                    "Failed to update section {}".format(xd["sectionname"]),
                    exc_info=True,
                )
        else:
            log.error("xd is not a dict: {}: {}".format(type(xd), xd), exc_info=True)
        return ret

    def myAccountList(self):
        """
        returns a list of tuples
          (account, expire timestamp, expire string, default account)
        """
        accts = []
        defsect = self.getDefaultSection()
        if "alias" in defsect:
            defname = defsect["alias"]
        elif "section" in defsect:
            defname = defsect["section"]
        else:
            defname = "undefined"
        for section in self.ifn.titles():
            if section != "default":
                default = True if section == defname else False
                tsectd = self.ifn.getSectionItems(section)
                if "expires" in tsectd:
                    expstr = utils.displayExpires(
                        int(tsectd["expires"]), int(tsectd["duration"])
                    )
                    acct = (section, tsectd["expires"], expstr, default)
                    accts.append(acct)
        return accts

    def displayMyList(self):
        defsect = self.getDefaultSection()
        if "tokenexpires" in defsect:
            if int(defsect["tokenexpires"]) > 0:
                log.info(
                    "User Token {}".format(
                        utils.displayExpires(int(defsect["tokenexpires"]))
                    )
                )
        if "alias" in defsect:
            defname = defsect["alias"]
        elif "section" in defsect:
            defname = defsect["section"]
        else:
            defname = "undefined"
        for section in self.ifn.titles():
            if section != "default":
                defstr = "(DEFAULT)" if section == defname else ""
                tsectd = self.ifn.getSectionItems(section)
                if "expires" in tsectd:
                    expstr = utils.displayExpires(
                        int(tsectd["expires"]), int(tsectd["duration"])
                    )
                    log.info("{} {} {}".format(section, expstr, defstr))

    def requestList(self):
        jaccs = None
        endpoint = self.getEndpoint()
        defsect = self.getDefaultSection()
        params = {"text": "--list"}
        params["user_name"] = defsect["username"]
        params["token"] = defsect["usertoken"]
        params["response_url"] = "ignoreme"
        params["useragent"] = "cca " + version
        r = requests.post(endpoint, data=params)
        if 200 == r.status_code:
            if r.text == "null":
                log.warning("No response")
            else:
                jmm = r.json()
                d = ast.literal_eval(jmm["text"])
                jaccs = d.get("accountlist")
        else:
            log.warning("status: {} response: {}".format(r.status_code, r.text))
        return jaccs

    def deleteAccount(self, account):
        if account in self.ifn.titles():
            if self.verbose > 0:
                log.info("Deleting account {}.".format(account))
            self.ifn.deleteSection(account)

    def parkAccount(self, account):
        if account in self.ifn.titles():
            secta = self.ifn.getSectionItems(account)
            if account not in self.pfn.titles():
                self.pfn.add_section(account)
            self.pfn.updateSection(account, secta, True)
            self.ifn.deleteSection(account)
            log.info("{} account has been parked".format(account))

    def unparkAccount(self, account):
        if account in self.pfn.titles():
            secta = self.pfn.getSectionItems(account)
            if account not in self.ifn.titles():
                self.ifn.add_section(account)
            self.ifn.updateSection(account, secta, True)
            self.pfn.deleteSection(account)
            self.renewSection(account)

    def listParkAccounts(self):
        slst = []
        for title in self.pfn.titles():
            slst.append(title)
        slst.sort()
        return slst
