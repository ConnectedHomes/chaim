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
chaim functions for both CLI and Slack
"""

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def getDefaultValue(xdict, key, default=""):
    ret = default
    if key in xdict:
        ret = xdict[key]
    return ret


def addToReqBody(rbody, key, val):
    ret = rbody
    if len(ret) > 0:
        ret += "&"
    ret += key
    ret += "="
    ret += str(val)
    return ret


def addToSeperatedString(istr, astr, seperator="/"):
    if len(istr):
        ostr = istr + astr if istr.endswith(seperator) else istr + seperator + astr
    else:
        ostr = astr
    return ostr


def addToOutStr(ostr, key, val, newline=True):
    log.debug("in addToOutString")
    log.debug("{} {} {} {}".format(ostr, key, val, newline))
    nl = "\n" if newline else ""
    if len(ostr) == 0:
        msg = "{} = {}".format(key, val)
    else:
        msg = "{}{}{} = {}".format(ostr, nl, key, val)
    return msg


def setDebug():
    log.setLevel(logging.DEBUG)


def usage():
    """
    outputs useful usage information for the slack command
    """
    xstr = """
    ```
    /chaim <command or account[name|number]>, [<role>], [duration seconds]

    Commands:
      count, --count, -c        show a count of chaim usage over the last 2 months
      help, --help, -h          This help text
      initshow, --initshow, -i  show your init params for the chaim cli
      list, --list, -l          List the account names
      roles, --roles, -r        List of Roles and Role Abbreviations
      whoskey, --whoskey, -w    Who was that key issued to?
      version, --version, -v    show chaim version

    Notes:
      As some account names can have spaces in them, you need to delimit
      the account name from the role by a comma. Don't put the account
      name in quotes as this function only does a simple is in [list]
      comparison, which will never find your account if it is in quotes.

      Rather than the full name you can use the account number instead.

      If you don't supply a role then you get CrossAccountReadOnly.

      Duration is in hours or seconds, default is 900, and is the session
      duration passed to AWS when requesting the signin token for a UI session.
      The subsequent UI URL will be valid for this length of time for first use.
      Values <13 are in hours, >12 are seconds.
      The value is constrained to the following limits:
          >=900 seconds
          <=12 hours (43,200 seconds)

    Who's Key:
        /chaim -w <key> (note: seperated by a space, not a comma)
      ```
      """
    return xstr
