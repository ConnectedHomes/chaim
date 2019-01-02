import chaimlib.glue as glue
from chaimlib.botosession import BotoSession

log = glue.log


class AccessKeyError(Exception):
    pass


class IamClient(BotoSession):
    def __init__(self, awsaccessid=None, awssecretkey=None, awsprofile=None, defaultsession=False, stoken=None):
        super().__init__(accessid=awsaccessid, secretkey=awssecretkey, theprofile=awsprofile,
                         usedefault=defaultsession, stoken=stoken)
        self.newClient('iam')
        self.currentkey = None
        self.user = None

    def testProfile(self):
        user = self.getKeys(username="sre.chaim")
        if type(user) is dict:
            if "keys" in user:
                log.debug("User: {}".format(user["Arn"]))
                return True
        return False

    def getUser(self, username):
        """returns a user dict

        This is intended to not be called standalone, but to be called by the
        getKeys() method, so that the user information is as complete as
        possible
        """
        try:
            user = self.client.get_user(UserName=username)
        except Exception as e:
            log.error("IamClient: Failed to retrieve username, are you actually connected?\n{}".format(e))
            return False
        return user["User"]

    def getKeys(self, username):
        """returns a user dict complete with registered access keys"""
        ret = False
        user = self.getUser(username)
        log.debug("user: {}".format(user))
        if user is not False:
            self.user = user
            try:
                keys = self.client.list_access_keys(UserName=self.user["UserName"])
                log.debug("keys: {}".format(keys))
                self.user["keys"] = keys["AccessKeyMetadata"]
                ret = self.user
            except Exception as e:
                log.error("Failed to obtain access key infomation for user: {}".format(self.user["UserName"]))
                log.error("Exception was {}".format(e))
        return ret

    # I'm not writing tests for the methods below as they
    # all fiddle with credentials. They all fail safe, so
    # your credentials are safe unless they do what they say they
    # are going to do.  Just use the rotateKeys method and
    # forget about whinging.  The dictionary it returns will
    # have your current, active key and secret information.
    def __delete_inactive_keys(self):
        """If the user has an inactive key, this will delete it

        sets the self.currentkey to the currently active key id
        so this must be run before generating a new key so that the
        old key can be deactivated easily.  Also, AWS only allows
        a user to have 2 keys at any one time (whether active or not).
        """
        res = True
        self.user = self.getKeys(username="sre.chaim")
        for key in self.user["keys"]:
            if key["Status"] == "Active":
                self.currentkey = key["AccessKeyId"]
            elif key["Status"] == "Inactive":
                try:
                    self.client.delete_access_key(AccessKeyId=key["AccessKeyId"], UserName=self.user["UserName"])
                except Exception as e:
                    msg = "An error occurred deleting the inactive access key: {}".format(key["AccessKeyId"])
                    msg += " for user {}, the exception was: {}".format(self.user["UserName"], e)
                    log.error(msg)
                    res = False
        return res

    def __deactivate_current_key(self):
        """This will deactivate the users currently active key

        This must be called after generating a new key, so that the
        user only has one active key at any one time
        """
        res = True
        if self.currentkey is not None:
            try:
                self.client.update_access_key(AccessKeyId=self.currentkey, UserName=self.user["UserName"],
                                              Status="Inactive")
            except Exception as e:
                msg = "Failed to de-activate the current key {} for user{}.".format(self.currentkey,
                                                                                    self.user["UserName"])
                msg += " Error was{}".format(e)
                log.error(msg)
                res = False
        return res

    def __generate_new_key(self):
        key = False
        try:
            key = self.client.create_access_key(UserName=self.user["UserName"])
            # rebuild the user dictionary
            # I know, but it saves dicking around deleting keys from
            # the user dictionary and deactivating the current one later on
            # this does it all in one line, te he he.
            self.getKeys(username="sre.chaim")
        except Exception as e:
            log.error("Exception generating a new key for user {}, {}".format(self.user["UserName"], e))
        return key

    def rotateKeys(self):
        """This will leave the user with a new, active key

        It first deletes any inactive key,
        then generates a new active key,
        the de-activates the original key.
        returns a dictionary:
        {
        "UserName": the users name
        "Arn": the arn of the user
        "Keys": hash of key dicts.
            [{
            "AccessKeyId": access key id
            "SecretAccessKey": secret access key id
            "Status": Active | Inactive
            },
            {...}]
        """
        key = None
        try:
            if self.__delete_inactive_keys() is False:
                raise AccessKeyError("AccessKeyError: Failure to delete inactive key")
            key = self.__generate_new_key()
            if key is False:
                raise AccessKeyError("AccessKeyError: Failure to generate a new key")
            if self.__deactivate_current_key() is False:
                raise AccessKeyError("AccessKeyError: Failure to de-activate the users current key")
        except Exception as e:
            log.error("An error occurred while attempting key rotation, see logs.")
            log.error("Exception was {}".format(e))
        return key
