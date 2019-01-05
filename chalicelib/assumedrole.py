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
"""
Uses an AssumedRoleObject from STS to obtain
signin tokens and session urls

requires python3
"""
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4 foldmethod=indent:

from urllib.parse import quote_plus
import json
import requests
import chalicelib.glue as glue

log = glue.log


class TokenBuildError(Exception):
    pass


class AssumedRole():
    def __init__(self, arobject, loglevel=None):
        self.aro = arobject
        if loglevel is not None:
            log.setLevel = loglevel
        self.creds = None
        self.accessid = None
        self.sessionkey = None
        self.sessionToken = None
        self.ok = self.testself()

    def testself(self):
        res = False
        if type(self.aro) is dict:
            if "Credentials" in self.aro:
                self.creds = self.aro["Credentials"]
            else:
                msg = '"Credentials" does not exist in assumed role object:'
                msg += " {}".format(self.aro)
                log.warning(msg)
            try:
                self.accessid = self.creds["AccessKeyId"]
                self.sessionkey = self.creds["SecretAccessKey"]
                self.sessionToken = self.creds["SessionToken"]
            except Exception as e:
                log.warning('key does not exist in credentials: {}'.format(e))
            res = True
        return res

    def getCreds(self):
        creds = None
        if self.ok:
            creds = {"sessionId": self.accessid,
                     "sessionKey": self.sessionkey,
                     "sessionToken": self.sessionToken}
        return creds

    def buildRequestUrl(self, initialparams):
        url = ""
        for param in initialparams:
            if len(url) == 0:
                url = "?{}={}".format(param, initialparams[param])
            else:
                url += "&{}={}".format(param, initialparams[param])
        return "https://signin.aws.amazon.com/federation{}".format(url)

    def getSigninToken(self, duration):
        signtoken = None
        creds = self.getCreds()
        if self.ok:
            session = quote_plus(json.dumps(creds))
            params = {"Action": "getSigninToken",
                      "SessionDuration": duration,
                      "Session": session}
            url = self.buildRequestUrl(params)
            log.debug("request url: {}".format(url))
            try:
                res = requests.get(url)
                if 200 == res.status_code:
                    signtoken = json.loads(res.text)
                else:
                    msg = "status: {} ".format(res.status_code)
                    msg += "failure obtaining signin token: "
                    msg += res.text
                    raise(TokenBuildError(msg))
            except Exception as e:
                log.error("Exception requesting a signin token: {}".format(e))
        return signtoken

    def getLoginUrl(self, duration):
        st = self.getSigninToken(duration)
        if st is not None:
            log.info("Signin token issued for {} seconds".format(duration))
            dest = quote_plus("https://eu-west-1.console.aws.amazon.com/")
            params = {"Action": "login", "Issuer": "hivehome.com",
                      "Destination": dest, "SigninToken": st["SigninToken"]}
            return self.buildRequestUrl(params)
        else:
            log.warning("Failed to obtain a signin token")
            return False
