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
chaim module for click based chaim cli (cca)

This is the module that does all the work
"""

import sys
import subprocess
import click
import time
import requests
import json
import base64
import pyperclip
import cca.cliutils as cliutils
import ast
from cca import __version__ as ccaversion


class UnmanagedAccount(Exception):
    pass


class NoUrl(Exception):
    pass


def getDefaultSection(ifn):
    ret = None
    if "default" in ifn.titles():
        ret = ifn.getSectionItems("default")
    else:
        ifn.add_section("default")
        ret = ifn.getSectionItems("default")
    return ret


def getDefaultAccount(ifn):
    ret = None
    defsect = getDefaultSection(ifn)
    if "section" in defsect:
        ret = defsect["alias"] if "alias" in defsect else defsect["section"]
    return ret


def getEndpoint(ifn):
    defsect = getDefaultSection(ifn)
    endpoint = "https://{}.".format(defsect['api'])
    endpoint += "execute-api.{}.".format(defsect['region'])
    endpoint += "amazonaws.com/{}/".format(defsect['stage'])
    return endpoint


def renewSection(section, ifn):
    """renews the config file section named 'section'"""
    defsect = getDefaultSection(ifn)
    if section in ifn.titles():
        sect = ifn.getSectionItems(section)
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
            return requestKeys(account, role, duration, alias, ifn, setregion, default, terrible)
        else:
            raise UnmanagedAccount("ignoring " + section + " as it is not managed by cca")
    else:
        return False


def requestKeys(account, role, duration, accountalias, ifn, setregion, default=False, terrible=False):
    ret = False
    defsect = getDefaultSection(ifn)
    if account == "NOT SET":
        return ret
    if len(accountalias) == 0:
        accountalias = account
    click.echo("account: {}, alias: {}, role: {}, duration: {}".format(account, accountalias, role, duration))
    params = {"text": "{},{},{}".format(account, role, duration)}
    params["user_name"] = defsect["username"]
    params["token"] = defsect["usertoken"]
    params["response_url"] = "ignoreme"
    params["useragent"] = "cca " + ccaversion
    if "slackid" in defsect:
        params["user_id"] = defsect["slackid"]
    if "workspaceid" in defsect:
        params["team_id"] = defsect["workspaceid"]
    endpoint = getEndpoint(ifn)
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
                    click.echo("Error: {}: {}".format(sc, d["text"]), err=True)
                else:
                    ret = storeKeys(d["text"], duration, role, accountalias, ifn, setregion, default, terrible)
                    click.echo("{} retrieval took {} seconds.".format(accountalias,taken))
        else:
            click.echo("d is not a dict", err=True)
    else:
        click.echo("status: {} response: {}".format(r.status_code, r.text), err=True)
    return ret


def storeKeys(text, duration, role, accountalias, ifn, setregion=False, default=False, terrible=False):
    ret = False
    defsect = getDefaultSection(ifn)
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
        if accountalias not in ifn.titles():
            # log.debug("adding account: {}".format(accountalias))
            ifn.add_section(accountalias)
        if ifn.updateSection(accountalias, dd, True):
            click.echo("Updated section {} with new keys".format(xd["sectionname"]))
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
                    if ifn.updateSection("default", defsect, True):
                        click.echo("updated default account")
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
                if ifn.updateSection("default", defsect, True):
                    click.echo("updated default account")
        else:
            click.echo("Failed to update section {}".format(xd["sectionname"]), err=True)
    else:
        click.echo("xd is not a dict: {}: {}".format(type(xd), xd), err=True)
    return ret


def requestUrl(account, ifn):
    ret = False
    defsect = getDefaultSection(ifn)
    endpoint = getEndpoint(ifn)
    try:
        if account in ifn.titles():
            sect = ifn.getSectionItems(account)
            accountname = sect["accountname"]
            now = int(time.time())
            exp = int(sect.get("expires"))
            duration = exp - now
            if duration > 0:
                params = {}
                params["accesskey"] = sect.get("aws_access_key_id")
                params["secret"] = sect.get("aws_secret_access_key")
                params["session"] = sect.get("aws_session_token")
                params["duration"] = duration
                params["username"] = defsect["username"]
                params["account"] = accountname
                params["useragent"] = "cca " + ccaversion
                print("sending to {} data: {}".format(endpoint + "gui", params))
                r = requests.post(endpoint + "gui", data=params)
                if 200 == r.status_code:
                    if r.text == "null":
                        print("no response")
                    else:
                        jmm = r.json()
                        if jmm["text"]:
                            dmm = json.loads(jmm["text"].replace("'", '"'))
                            ret = dmm["url"]
                else:
                    print("status: {} response: {}".format(r.status_code, r.text))
            else:
                print("account {} has expired".format(account))
        else:
            print("account {} not found".format(account))
    except Exception as e:
        print("Exception in requestUrl: {} {}".format(type(e).__name__, e))
    return [ret, duration]


def doUrl(account, ifn, browser=False, logout=False):
    if len(account) == 0:
        account = [getDefaultAccount(ifn)]
    if account is None:
        click.echo("account name required or no default account set.")
        return
    acct = account[0]
    if not ifn.sectionExists(acct):
        click.echo("account {} not recognised.".format(acct))
        return
    renewSection(acct, ifn)
    sect = ifn.getSectionItems(acct)
    url = None
    if "gui_url" in sect:
        if sect["gui_url"] != "notset":
            url = sect["gui_url"]
        else:
            raise NoUrl("gui_url == notset")
    else:
        raise NoUrl("gui_url not set in credentials")
    pyperclip.copy(url)
    expires = int(sect["expires"]) - cliutils.getNow()
    msg = cliutils.displayHMS(expires)
    cmsg = "URL copied to clipboard for account {}\nExpires: {}".format(acct, msg)
    cmd = "open" if sys.platform == "darwin" else "xdg-open"
    if browser:
        try:
            subprocess.Popen([cmd, url])
            click.echo("GUI session opened for account {}\nExpires: {}".format(acct, msg))
        except OSError:
            click.echo(cmsg)
    elif logout:
        try:
            logouturl = "https://signin.aws.amazon.com/oauth?Action=logout"
            subprocess.Popen([cmd, logouturl])
            click.echo("Loging out of current session (if any)")
            time.sleep(1)
            subprocess.Popen([cmd, url])
            click.echo("GUI session opened for account {}\nExpires: {}".format(acct, msg))
        except OSError:
            click.echo(cmsg)
    else:
        click.echo(cmsg)


def askInit(ifn):
    reqkeys = ["api", "username", "usertoken", "tokenexpires", "stage", "region", "slackid", "workspaceid"]
    defsect = getDefaultSection(ifn)
    for key in reqkeys:
        if key in ["usertoken", "tokenexpires"]:
            defsect[key] = input("{}: ".format(key))
        else:
            if key in defsect:
                tval = input("{} ({}): ".format(key, defsect[key]))
                if len(tval) > 0:
                    defsect[key] = tval
            else:
                defsect[key] = input("{}: ".format(key))
    ifn.updateSection("default", defsect, True)
    estr = cliutils.displayHMS(int(defsect["tokenexpires"]) - int(time.time()), True)
    click.echo("cca has been re-initialised.\nYour token will expire in {}.".format(estr))


def doInit(initstr, ifn):
    defsect = getDefaultSection(ifn)
    if len(initstr) > 0:
        istr = initstr[0]
        bl = base64.urlsafe_b64decode(istr.encode('utf-8')).decode('utf-8').split("&")
        for param in bl:
            pl = param.split("=")
            if pl[0] == "expires":
                defsect["tokenexpires"] = pl[1]
            else:
                defsect[pl[0]] = pl[1]
        ifn.updateSection("default", defsect, True)
        estr = cliutils.displayHMS(int(defsect["tokenexpires"]) - int(time.time()), True)
        click.echo("cca has been re-initialised.\nYour token will expire in {}.".format(estr))
    else:
        askInit(ifn)


def displayMyList(ifn):
    defsect = getDefaultSection(ifn)
    if "tokenexpires" in defsect:
        if int(defsect["tokenexpires"]) > 0:
            click.echo("User Token {}".format(cliutils.displayExpires(int(defsect["tokenexpires"]))))
    if 'alias' in defsect:
        defname = defsect['alias']
    elif 'section' in defsect:
        defname = defsect["section"]
    else:
        defname = "undefined"
    for section in ifn.titles():
        if section != "default":
            defstr = "(DEFAULT)" if section == defname else ""
            tsectd = ifn.getSectionItems(section)
            if "expires" in tsectd:
                expstr = cliutils.displayExpires(int(tsectd["expires"]), int(tsectd["duration"]))
                click.echo("{} {} {}".format(section, expstr, defstr))


def requestList(ifn):
    endpoint = getEndpoint(ifn)
    defsect = getDefaultSection(ifn)
    params = {"text": "--list"}
    params["user_name"] = defsect["username"]
    params["token"] = defsect["usertoken"]
    params["response_url"] = "ignoreme"
    params["useragent"] = "cca " + ccaversion
    r = requests.post(endpoint, data=params)
    if 200 == r.status_code:
        if r.text == 'null':
            print("No response")
        else:
            jmm = r.json()
            d = ast.literal_eval(jmm["text"])
            jaccs = d.get("accountlist")
            for row in jaccs:
                print("{} {}".format(row[0], row[1]))
    else:
        print("status: {} response: {}".format(r.status_code, r.text))


def deleteAccount(account, ifn):
    if account in ifn.titles():
        click.echo("Deleting account {}.".format(account))
        ifn.deleteSection(account)


def parkAccount(account, ifn, pfn):
    if account in ifn.titles():
        secta = ifn.getSectionItems(account)
        if account not in pfn.titles():
            pfn.add_section(account)
        pfn.updateSection(account, secta, True)
        ifn.deleteSection(account)
        print("{} account has been parked".format(account))


def unparkAccount(account, ifn, pfn):
    if account in pfn.titles():
        secta = pfn.getSectionItems(account)
        if account not in ifn.titles():
            ifn.add_section(account)
        ifn.updateSection(account, secta, True)
        pfn.deleteSection(account)
        renewSection(account, ifn)


def listParkAccounts(pfn):
    slst = []
    for title in pfn.titles():
        slst.append(title)
    slst.sort()
    for title in slst:
        print(title)
