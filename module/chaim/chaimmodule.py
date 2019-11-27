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
import pyperclip
import chaim.logging as LOG
import chaim.utils as utils
import chaim.inifile as inifile
from chaim.errors import errorRaise
from chaim.errors import errorNotify
from chaim.errors import errorExit
from chaim import __version__ as version

log = LOG.log
LOG.setConsoleOut()
LOG.setInfo()

class UnmanagedAccount(Exception):
    pass


class NoUrl(Exception):
    pass


class Chaim(object):
    def __inti__(self, account, role, duration=1):
        self.root = os.path.expanduser("~/.aws")
        self.credsfn = self.root + "/credentials"
        self.parkfn = self.root + "/chaim-parked"
        self.ifn = inifile(self.credsfn, takebackup=False)
        self.pfn = inifile(self.parkfn, takebackup=False)
        self.account = account
        self.role = role
        self.duration = duration

    def __enter__(self):
        pass

    def _exit__(self):
        pass

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
        endpoint = "https://{}.".format(defsect['api'])
        endpoint += "execute-api.{}.".format(defsect['region'])
        endpoint += "amazonaws.com/{}/".format(defsect['stage'])
        return endpoint

    def renewSection(self, section):
        """renews the config file section named 'section'"""
        defsect = self.getDefaultSection()
        if section in self.ifn.titles():
            sect = self.ifn.getSectionItems(section)
            if "accountname" in sect:
                account = sect["accountname"]
                duration = sect["duration"]
                role = sect["role"]
                alias = section
                default = False
                if "alias" in defsect:
                    default = True if defsect["alias"] == section else False
                if "region" in sect:
                    setregion = sect["region"]
                terrible = True if "aws_security_token" in sect else False
                return self.requestKeys(account, role, duration, alias, setregion, default, terrible)
            else:
                raise UnmanagedAccount("ignoring " + section + " as it is not managed by cca")
        else:
            return False

    def requestKeys(self, account, role, duration, accountalias, setregion, default=False, terrible=False):
        ret = False
        defsect = self.getDefaultSection()
        if account == "NOT SET":
            return ret
        if len(accountalias) == 0:
            accountalias = account
        log.info("account: {}, alias: {}, role: {}, duration: {}".format(account, accountalias, role, duration))
        params = {"text": "{},{},{}".format(account, role, duration)}
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
                        log.error("Error: {}: {}".format(sc, d["text"]), err=True)
                    else:
                        ret = self.storeKeys(d["text"], duration, role, accountalias, setregion, default, terrible)
                        log.info("{} retrieval took {} seconds.".format(accountalias,taken))
            else:
                log.error("d is not a dict", err=True)
        else:
            log.info("status: {} response: {}".format(r.status_code, r.text), err=True)
        return ret

    def storeKeys(self, text, duration, role, accountalias, setregion=False, default=False, terrible=False):
        ret = False
        defsect = self.getDefaultSection()
        xd = json.loads(text.replace("'", '"'))
        if isinstance(xd, dict):
            dd = {}
            dd["aws_access_key_id"] = xd["accesskeyid"]
            dd["aws_secret_access_key"] = xd["secretkey"]
            dd["aws_session_token"] = xd["sessiontoken"]
            if terrible:
                dd["aws_security_token"] = xd["sessiontoken"]
            dd["region"] = defsect["region"]
            dd["expires"] = str(xd["expires"])
            dd["expstr"] = xd["expiresstr"]
            dd["duration"] = str(duration)
            dd["gui_url"] = xd["url"]
            dd["role"] = role
            dd["accountname"] = xd["sectionname"]
            if setregion:
                dd["region"] = setregion
            if accountalias not in self.ifn.titles():
                # log.debug("adding account: {}".format(accountalias))
                self.ifn.add_section(accountalias)
            if self.ifn.updateSection(accountalias, dd, True):
                log.info("Updated section {} with new keys".format(xd["sectionname"]))
                ret = True
                if "section" in defsect:
                    if defsect["section"] == xd["sectionname"]:
                        defsect["aws_access_key_id"] = xd["accesskeyid"]
                        defsect["aws_secret_access_key"] = xd["secretkey"]
                        defsect["aws_session_token"] = xd["sessiontoken"]
                        if terrible:
                            defsect["aws_security_token"] = xd["sessiontoken"]
                        defsect["alias"] = accountalias
                        defsect["expires"] = str(xd["expires"])
                        if self.ifn.updateSection("default", defsect, True):
                            log.info("updated default account")
                            default = False
                if default:
                    defsect["aws_access_key_id"] = xd["accesskeyid"]
                    defsect["aws_secret_access_key"] = xd["secretkey"]
                    defsect["aws_session_token"] = xd["sessiontoken"]
                    if terrible:
                        defsect["aws_security_token"] = xd["sessiontoken"]
                    defsect["section"] = xd["sectionname"]
                    defsect["alias"] = accountalias
                    defsect["expires"] = str(xd["expires"])
                    if self.ifn.updateSection("default", defsect, True):
                        log.info("updated default account")
            else:
                log.error("Failed to update section {}".format(xd["sectionname"]), err=True)
        else:
            log.error("xd is not a dict: {}: {}".format(type(xd), xd), err=True)
        return ret

    def displayMyList(self):
        defsect = self.getDefaultSection()
        if "tokenexpires" in defsect:
            if int(defsect["tokenexpires"]) > 0:
                log.info("User Token {}".format(utils.displayExpires(int(defsect["tokenexpires"]))))
        if 'alias' in defsect:
            defname = defsect['alias']
        elif 'section' in defsect:
            defname = defsect["section"]
        else:
            defname = "undefined"
        for section in self.ifn.titles():
            if section != "default":
                defstr = "(DEFAULT)" if section == defname else ""
                tsectd = self.ifn.getSectionItems(section)
                if "expires" in tsectd:
                    expstr = utils.displayExpires(int(tsectd["expires"]), int(tsectd["duration"]))
                    log.info("{} {} {}".format(section, expstr, defstr))

    def requestList(self):
        endpoint = self.getEndpoint()
        defsect = self.getDefaultSection()
        params = {"text": "--list"}
        params["user_name"] = defsect["username"]
        params["token"] = defsect["usertoken"]
        params["response_url"] = "ignoreme"
        params["useragent"] = "cca " + version
        r = requests.post(endpoint, data=params)
        if 200 == r.status_code:
            if r.text == 'null':
                log.info("No response")
            else:
                jmm = r.json()
                d = ast.literal_eval(jmm["text"])
                jaccs = d.get("accountlist")
                for row in jaccs:
                    log.info("{} {}".format(row[0], row[1]))
        else:
            log.info("status: {} response: {}".format(r.status_code, r.text))

    def deleteAccount(self, account):
        if account in self.ifn.titles():
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
        for title in slst:
            log.info(title)

