"""AWS Cognito-IDP client functions"""

from chaimlib.botosession import BotoSession
import logging
import re

log = logging.getLogger(__name__)


class CognitoClient(BotoSession):
    def __init__(self, awsaccessid=None, awssecretkey=None, awsprofile=None,
                 defaultsession=True, stoken=None):
        super().__init__(accessid=awsaccessid, secretkey=awssecretkey,
                         theprofile=awsprofile, usedefault=defaultsession,
                         stoken=stoken)
        self.newClient('cognito-idp')

    def listPools(self):
        resp = self.client.list_user_pools(MaxResults=30)
        data = resp["UserPools"]
        while resp.get("NextToken"):
            resp = self.client.list_user_pools(MaxResults=30,
                                               NextToken=resp["NextToken"])
            data.extend(resp["UserPools"])
        return data

    def listUsers(self, poolid, efilter=None):
        if efilter is not None:
            resp = self.client.list_users(Limit=30, UserPoolId=poolid,
                                          Filter=efilter)
        else:
            resp = self.client.list_users(Limit=30, UserPoolId=poolid)
        data = resp["Users"]
        while resp.get("PaginationToken"):
            if efilter is not None:
                resp = self.client.list_users(Limit=30, UserPoolId=poolid, PaginationToken=resp["PaginationToken"], Filter=efilter)  # nopep8
            else:
                resp = self.client.list_users(Limit=30, UserPoolId=poolid, PaginationToken=resp["PaginationToken"])  # nopep8
            data.extend(resp["Users"])
        return data

    def enabledUserList(self, poolid):
        users = {}
        tmp = self.listUsers(poolid)
        for user in tmp:
            if user["Enabled"]:
                for attr in user["Attributes"]:
                    group = []
                    if attr["Name"] == "custom:Team":
                        group = attr["Value"].split(",")
                        break
                users[user["Username"]] = group
        return users

    def adminGetUser(self, poolid, username):
        resp = {}
        try:
            resp = self.client.admin_get_user(Username=username,
                                              UserPoolId=poolid)
        except Exception as e:
            log.warning("Exception when retrieving user details for user {} in pool {}: {}".format(username, poolid, e))  # nopep8
        return resp

    def findUserByEmail(self, poolid, emailaddr):
        """
        pass in an emailaddress or just the username
        """
        xuser = None
        junk = emailaddr.split('@')
        ename = junk[0]
        rr = re.compile(ename.lower(), re.I)
        # this looks for an email address beginning with the ename
        efilt = "email ^= \"{}\"".format(ename)
        users = self.listUsers(poolid, efilt)
        for user in users:
            if "Attributes" in user:
                for attr in user["Attributes"]:
                    if attr["Name"] == "email":
                        xatt = attr["Value"].split('@')
                        res = rr.search(xatt[0])
                        if res is not None:
                            xuser = user
                            break
                        # xname = xatt[0].lower()
                        # if xname == ename.lower():
                        #     xuser = user
                        #     break
        return xuser
