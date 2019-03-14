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
import chalicelib.glue as glue
from chalicelib.utils import Utils
from urllib.parse import parse_qs

log = glue.log


class BadCommandStr(Exception):
    pass


class CommandParse():
    def __init__(self, rawbody, roledict=None, blankbody=False):
        self.dolist = False
        self.dohelp = False
        self.doversion = False
        self.dowhoskey = False
        self.doinitshow = False
        self.whoskey = None
        self.keyinit = False
        self.doshowroles = False
        self.docountusers = False
        self.doidentify = False
        self.docommand = False
        self.roledict = roledict
        self.apiid = None
        self.slackid = None
        log.debug("Command parse entry")
        log.debug("rawbody: {}".format(rawbody))
        self.parsed = parse_qs(rawbody)
        log.debug("parsed: {}".format(self.parsed))
        self.blankbody = blankbody
        self.username = self.extractField('user_name')
        self.slackid = self.extractField('user_id')
        self.incomingtoken = self.extractField('token')
        log.debug("token: {}".format(self.incomingtoken))
        self.responseurl = self.extractField('response_url')
        self.stage = self.extractField("stage")
        self.useragent = self.extractField("useragent")
        log.debug("stage: {}".format(self.stage))
        if "keyinit" in self.parsed:
            self.duration = 900
            self.keyinit = True
            self.blankbody = True
            self.apiid = self.extractField("apiid")
            self.docommand = True
        elif "identify" in self.parsed:
            self.duration = 900
            self.doidentify = True
            self.blankbody = True
            self.apiid = self.extractField("apiid")
            self.docommand = True
        else:
            if not self.blankbody:
                self.parseCommandText(self.extractField('text'))
                self.roleAliasToRole()

    def extractField(self, field):
        ret = xf = None
        if "b'" + field in self.parsed:
            xf = "b'" + field
        elif field in self.parsed:
            xf = field
        if xf is not None:
            tmp = self.parsed.get(xf)
            if isinstance(tmp, list):
                ret = tmp[0].strip()
            else:
                ret = self.parsed.get(xf).strip()
        return ret

    def parseCommandText(self, cmdtext):
        self.duration = 900
        self.rolealias = 'rro'
        fields = cmdtext.split(',')
        cn = len(fields)
        self.accountname = fields[0].strip()
        if self.accountname in ["--list", "-l", "list"]:
            self.dolist = True
            self.docommand = True
            self.blankbody = True
        elif self.accountname in ["--help", "-h", "help"]:
            self.dohelp = True
            self.docommand = True
            self.blankbody = True
        elif self.accountname in ["--version", "-v", "version"]:
            self.doversion = True
            self.docommand = True
            self.blankbody = True
        elif self.accountname in ["--initshow", "-i", "initshow"]:
            self.doinitshow = True
            self.apiid = self.extractField("apiid")
            self.docommand = True
            self.blankbody = True
        elif self.accountname in ["--roles", "-r", "roles"]:
            self.doshowroles = True
            self.docommand = True
            self.blankbody = True
        elif self.accountname in ["--count", "-c", "count"]:
            self.docountusers = True
            self.docommand = True
            self.blankbody = True
        elif " " in self.accountname:
            fields = self.accountname.split(" ")
            if fields[0] in ["--whoskey", "-w", "whoskey"]:
                self.dowhoskey = True
                self.docommand = True
                self.whoskey = fields[1]
                self.blankbody = True
        else:
            self.durationAndRole(fields, cn)

    def durationAndRole(self, fields, cn):
        if cn > 2:
            try:
                self.duration = int(fields[2].strip())
                self.rolealias = fields[1].strip()
            except ValueError:
                try:
                    self.duration = int(fields[1].strip())
                    self.rolealias = fields[2].strip()
                except ValueError:
                    raise BadCommandStr("Failed to parse command")
        elif cn > 1:
            self.rolealias = fields[1].strip()
        if self.duration <= 12 and self.duration >= 1:
            self.duration = self.duration * 3600
        elif self.duration < 900:
            self.duration = 900
        elif self.duration > 43200:
            self.duration = 43200
        ut = Utils()
        self.durationstr = ut.displayHMS(self.duration)

    def roleAliasToRole(self):
        if self.roledict is not None and self.rolealias in self.roledict:
            self.role = self.roledict[self.rolealias]
        else:
            if len(self.rolealias) == 3:
                if self.rolealias == "rro":
                    self.role = "CrossAccountReadOnly"
                elif self.rolealias == "mpu":
                    self.role = "CrossAccountPowerUser"
                elif self.rolealias == "spu":
                    self.role = "CrossAccountSysAdmin"
                elif self.rolealias == "apu":
                    self.role = "CrossAccountAdminUser"
                else:
                    self.role = None
            else:
                self.role = self.rolealias

    def requestDict(self):
        rdict = {"username": self.username}
        rdict["incomingtoken"] = self.incomingtoken
        rdict["responseurl"] = self.responseurl
        rdict["stage"] = self.stage
        rdict["useragent"] = self.useragent
        rdict["slackid"] = self.slackid
        if self.apiid is not None:
            rdict["apiid"] = self.apiid
        if not self.blankbody:
            rdict["duration"] = self.duration
            rdict["rolealias"] = self.rolealias
            rdict["role"] = self.role
            rdict["accountname"] = self.accountname
        log.debug("built request dictionary: {}".format(rdict))
        return rdict
