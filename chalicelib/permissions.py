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
from chalicelib.cognitoclient import CognitoClient
from chalicelib.paramstore import ParamStore
from chalicelib.slackiamdb import SlackIamDB
from chalicelib.slackiamdb import DBNotConnected
from chalicelib.utils import Utils
import chalicelib.glue as glue

log = glue.log


class IncorrectCredentials(Exception):
    pass


class DataNotFound(Exception):
    pass


class Permissions():
    def __init__(self, secretpath="", testdb=False, quick=False,
                 stagepath="", missing=False):
        log.debug("Permissions Entry")
        self.missing = missing
        self.spath = secretpath
        if len(stagepath) == 0:
            stagepath = "prod"
        # self.ps = ParamStore(env=stagepath)
        self.ps = ParamStore()
        plist = ["snstopicarn", "slackapitoken", "dbhost", "dbrouser", "dbdb",
                 "dbropass", "dbrwuser", "dbrwpass", "poolid", "slacktoken"]
        self.params = self.ps.getParams(plist, environment=stagepath)
        if len(self.params) is 0:
            raise IncorrectCredentials("failed to retrieve my parameters")
        self.topicarn = self.params["snstopicarn"]
        if not quick:
            self.fromslack = False
            self.connectDB(testdb)
            self.slackapitoken = self.params["slackapitoken"]

    def connectDB(self, testdb=False):
        if testdb:
            dbhost = "127.0.0.1"
        else:
            dbhost = self.params["dbhost"]
        dbrouser = self.params["dbrouser"]
        dbropass = self.params["dbropass"]
        dbrwuser = self.params["dbrwuser"]
        dbrwpass = self.params["dbrwpass"]
        dbdb = self.params["dbdb"]
        if dbhost is not None:
            self.sid = SlackIamDB(dbhost, dbrouser, dbropass, dbdb)
            log.debug("Created db connection ok")
            self.rwsid = SlackIamDB(dbhost, dbrwuser, dbrwpass, dbdb)
            log.debug("Created rw db connection ok")
        else:
            self.sid = None
            self.rwsid = None

    def getEncKey(self, keyname, extrapath=None):
        param = None
        spath = self.spath if self.spath.endswith("/") else self.spath + "/"
        try:
            if extrapath is None:
                param = self.ps.getEString(spath + keyname)
            else:
                param = self.ps.getEString(spath + extrapath + keyname)
        except Exception as e:
            log.debug("parameter not found: {}".format(keyname))
            if not self.missing:
                log.error("parameter not found: {}".format(keyname))
                raise DataNotFound(e)
        return param

    def userNameFromSlackId(self, slackid):
        """returns the chaim username for the slackid"""
        try:
            username = self.singleField("awsusers","name","slackid","SlackID",slackid)
        except DataNotFound as e:
            emsg = "failed to obtain username from slackid: {}".format(slackid)
            log.error(emsg)
            raise DataNotFound(emsg)
        return username


    def userActive(self, username):
        ret = None
        msg = "User not found in Cognito DB: /{}\\".format(username)
        # TODO
        # usernames in secadmin cognito idp now appear to be of the form
        # bgch_User.Name@BGCHNET.CO.UK
        # .co.uk is lowercase
        # this may change back to 'user.name' eventually
        # hence uncomment this next line and comment the following one.
        un = username
        # un = "bgch_{}@BGCHNET.co.uk".format(username.title())
        poolid = self.params["poolid"]
        cc = CognitoClient()
        userinfo = cc.adminGetUser(poolid, un)
        log.debug("getuser returned: {}".format(userinfo))
        if isinstance(userinfo, dict):
            if "Enabled" in userinfo:
                log.debug("CC: userinfo: {}".format(userinfo))
                ret = userinfo["Enabled"]
            else:
                msg = "User not Enabled in Cognito DB: "
                msg += "{} ({})".format(username, un)
                raise DataNotFound(msg)
        else:
            raise DataNotFound(msg)
        return ret

    def checkToken(self, token, username):
        log.debug("token: {}, username: {}".format(token, username))
        ut = Utils()
        slacktoken = self.params["slacktoken"]
        if slacktoken == token:
            self.fromslack = True
            return True
        else:
            clitoken, expires = self.readUserToken(username)
            if token == clitoken:
                if expires > ut.getNow():
                    return True
                else:
                    raise(IncorrectCredentials("usertoken has expired"))
        raise(IncorrectCredentials("Invalid token"))
        return False

    def singleField(self, table, field, wfield, dataname, data,
                    notfoundOK=False):
        log.debug("getting single field for {}".format(field))
        if self.sid is not None:
            xdata = self.sid.singleField(table, field, "{}='{}'".format(wfield,
                                                                        data))
            if xdata is None:
                if notfoundOK:
                    log.debug("{} {} not found, continuing".format(dataname,
                                                                   data))
                    return xdata
                msg = self.createDataNotFoundMessage(dataname, data)
                log.error("single field not found: {}".format(field))
                log.error(msg)
                raise DataNotFound(msg)
            log.debug("found: {}".format(xdata))
            return xdata
        else:
            raise DBNotConnected("no connection to Database")

    def checkIDs(self, table, wfield, dataname, data, notfoundOK=False):
        return self.singleField(table, "id", wfield, dataname,
                                data, notfoundOK)

    def createDataNotFoundMessage(self, dataname, data):
        return "{} not found: {}".format(dataname, data)

    def addUpdateSlackUserId(self, username, slackuserid):
        if self.sid is not None:
            userid = self.checkIDs("awsusers", "name", "User", username)
        else:
            raise DBNotConnected("No connection to database")


    def userAllowed(self, username, account, role):
        log.debug("userAllowed test: {} {} {}".format(username, account, role))
        if self.sid is not None:
            userid = self.checkIDs("awsusers", "name", "User", username)
            ut = Utils()
            if ut.isNumeric(account):
                accountid = account
                self.derivedaccountname = self.sid.singleField("awsaccounts", "name", "id='{}'".format(accountid))
            else:
                accountid = self.checkIDs("awsaccounts", "name", "Account", account)
                log.debug("userAllowed: username: {}, account:{}, role: {}, accountid is {}".format(username,
                                                                                                    account, role,
                                                                                                    accountid))
                if accountid is None:
                    return [False, None]
                self.derivedaccountname = account
            roleid = self.checkIDs("awsroles", "name", "Role", role)
            sql = "select * from useracctrolemap where "
            sql += "accountid='{}'".format(accountid)
            sql += " and "
            sql += "roleid={}".format(roleid)
            sql += " and "
            sql += "userid={}".format(userid)
            rowa = self.sid.query(sql)
            if len(rowa):
                return [True, accountid]
            else:
                msg = "Permission not granted to {} in {} for {}".format(
                    username, account, role)
                raise DataNotFound(msg)
        else:
            raise DBNotConnected("No connection to Database")

    def updateKeyMap(self, username, accountid, accesskey, expires):
        try:
            if self.rwsid is not None:
                userid = self.checkIDs("awsusers", "name", "User", username)
                sql = "INSERT INTO keymap "
                sql += "(userid, accountid, accesskey, expires) VALUES "
                sql += "({}, '{}', '{}', {})".format(userid, accountid,
                                                     accesskey, expires)
                log.debug("key query: {}".format(sql))
                self.rwsid.insertQuery(sql)
            else:
                raise(DBNotConnected("no r/w connection to DB"))
        except Exception as e:
            log.error("error executing keymap insert query")
            raise DataNotFound(e)

    def cleanKeyMap(self, days=30, dryrun=False):
        afrows = 0
        tfr = 0
        try:
            sql = "select count(*) from keymap"
            rows = self.sid.query(sql)
            for row in rows:
                tfr = row[0]
            ut = Utils()
            then = ut.getNow() - (days * 24 * 60 * 60)
            if dryrun:
                sql = "select count(*) from keymap "
            else:
                sql = "delete from keymap "
            sql += "where expires < {}".format(then)
            if dryrun:
                rows = self.sid.query(sql)
                for row in rows:
                    afrows = row[0]
            else:
                afrows = self.rwsid.deleteQuery(sql)
        except Exception as e:
            msg = "A cleantKeyMap error occurred: {}: {}".format(type(e).__name__, e)
            log.error(msg)
            raise DataNotFound(msg)
        return [tfr, afrows]

    def updateUserToken(self, username, token, expires):
        ret = False
        try:
            if self.rwsid is not None:
                userid = self.checkIDs("awsusers", "name", "User",
                                       username, True)
                if userid is None:
                    sql = "INSERT INTO awsusers SET "
                    sql += "name='{}', ".format(username)
                else:
                    sql = "UPDATE awsusers SET "
                sql += "token='{}', tokenexpires={} ".format(token, expires)
                if userid is not None:
                    sql += "WHERE id={}".format(userid)
                    affectedrows = self.rwsid.updateQuery(sql)
                else:
                    affectedrows = self.rwsid.insertQuery(sql)
                if affectedrows == 1:
                    ret = True
            else:
                raise(DBNotConnected("no r/w connection to DB"))
            return ret
        except Exception as e:
            log.error("error executing usertoken insert query")
            raise DataNotFound(e)

    def readUserToken(self, username):
        token = expires = None
        try:
            sql = "select token, tokenexpires from awsusers where name='{}'".format(username)
            rows = self.sid.query(sql)
            if len(rows) > 0:
                token = rows[0][0]
                expires = rows[0][1]
        except Exception as e:
            msg = "A readUserToken error occurred: {}: {}".format(type(e).__name__, e)
            log.error(msg)
        return [token, expires]

    def checkUserToken(self, username, token):
        ut = Utils()
        try:
            dbtok, dbexp = self.readUserToken(username)
            if dbtok == token:
                if dbexp > ut.getNow():
                    return True
            return False
        except Exception as e:
            log.error("error executing check usertoken query")
            raise DataNotFound(e)

    def createUser(self, username):
        userid = 0
        sql = "insert into awsusers set name='{}'".format(username)
        af = self.rwsid.insertQuery(sql)
        if af == 1:
            userid = self.checkIDs("awsusers", "name", "User", username)
        return userid

    def findCognitoUser(self, username):
        ret = None
        msg = "User not found in Cognito DB: {}".format(username)
        cc = CognitoClient()
        userinfo = cc.findUserByEmail(self.params["poolid"], username)
        if isinstance(userinfo, dict):
            if "Enabled" in userinfo:
                log.debug("CC: userinfo: {}".format(userinfo))
                ret = userinfo["Enabled"]
            else:
                msg = "User not Enabled in Cognito DB: "
                msg += "{}".format(username)
                raise DataNotFound(msg)
        else:
            raise DataNotFound(msg)
        return ret

    def accountList(self):
        sql = "select * from awsaccounts order by name asc"
        return self.sid.query(sql)

    def whosKey(self, key):
        sql = "select k.accesskey, k.expires, u.name, a.name from keymap k, awsusers u, awsaccounts a where"
        sql += " k.accesskey='{}' ".format(key)
        sql += "and u.id=k.userid and a.id=k.accountid"
        row = self.sid.query(sql)
        if len(row) > 0:
            msg = "key: {}, search: {}".format(key, row)
            log.debug(msg)
        else:
            log.debug("key {} not found.".format(key))
        return row

    def roleAliasDict(self):
        radict = {}
        sql = "select alias, name from awsroles"
        rows = self.sid.query(sql)
        for row in rows:
            alias = row[0]
            name = row[1]
            radict[alias] = name
        log.debug("role aliases: {}".format(radict))
        return radict

    def lastupdated(self, userid, stamp, cli=False):
        if self.rwsid is not None:
            field = "lastslack" if cli is False else "lastcli"
            sql = "update awsusers set {}={} where id={}".format(field, stamp, userid)
            log.debug("update: {}".format(sql))
            self.rwsid.updateQuery(sql)

    def countLastSince(self, months=1):
        if self.sid is not None:
            ut = Utils()
            mnth = ut.displayWord(months, "Month")
            now = ut.getNow()
            then = now - (int(months) * 86400 * 30)
            sql = "select count(id) as cn from awsusers"
            rows = self.sid.query(sql)
            log.debug("sql returns {}".format(rows))
            allusers = rows[0][0]
            log.debug("allusers {}".format(allusers))
            sql = "select count(lastcli) as cn from awsusers where lastcli > " + str(then)
            rows = self.sid.query(sql)
            log.debug("sql returns {}".format(rows))
            lastcli = rows[0][0]
            sql = "select count(lastslack) as cn from awsusers where lastslack > " + str(then)
            rows = self.sid.query(sql)
            lastslack = rows[0][0]
            sql = "select count(lastcli) as cn from awsusers"
            sql += " where lastcli > " + str(then) + " and lastslack > " + str(then)
            rows = self.sid.query(sql)
            lastboth = rows[0][0]
            active = (int(lastslack) + int(lastcli)) - int(lastboth)
            inactive = int(allusers) - active
            msg = "Previous {}".format(mnth)
            msg += "\n{:<12}{:>5}".format("All:", allusers)
            msg += "\n{:<12}{:>5}".format("Active:", active)
            msg += "\n{:<12}{:>5}".format("Inactive:", inactive)
            msg += "\n{:<12}{:>5}".format("CLI:", lastcli)
            msg += "\n{:<12}{:>5}".format("Slack:", lastslack)
            msg += "\n{:<12}{:>5}".format("Both:", lastboth)
            return msg
        else:
            return "DB not connected"
