"""
AWS SSM Parameter Store client functions
"""

from chaimlib.botosession import BotoSession
import os
import chaimlib.glue as glue

log = glue.log


class ParamStore(BotoSession):
    def __init__(self, awsaccessid=None, awssecretkey=None,
                 awsprofile=None, stoken=None, usedefault=False, env="prod"):
        super().__init__(accessid=awsaccessid, secretkey=awssecretkey,
                         theprofile=awsprofile, stoken=stoken,
                         usedefault=usedefault)
        self.newClient('ssm')

    def putParam(self, pname, pvalue, ptype, pkeyid=None, pattern=None):
        """
        sets the named parameter
        returns the parameter version (how many times it has changed)
        see boto3 doc:
            http://boto3.readthedocs.io/en/latest/reference/services/ssm.html#SSM.Client.put_parameter
        """
        pversion = None
        try:
            """
            the indenting of this block may look silly
            but it passes the pep8 linter, so who am I to argue
            """
            if pattern is None and pkeyid is None:
                pversion = self.client.put_parameter(Name=pname,
                                                     Value=pvalue, Type=ptype,
                                                     Overwrite=True)
            elif pattern is None:
                pversion = self.client.put_parameter(Name=pname, Value=pvalue,
                                                     Type=ptype, KeyId=pkeyid,
                                                     Overwrite=True)
            elif pkeyid is None:
                pversion = self.client.put_parameter(Name=pname, Value=pvalue,
                                                     Type=ptype,
                                                     Overwrite=True,
                                                     AllowedPattern=pattern)
            else:
                pversion = self.client.put_parameter(Name=pname, Value=pvalue,
                                                     Type=ptype, KeyId=pkeyid,
                                                     Overwrite=True,
                                                     AllowedPattern=pattern)
        except Exception as e:
            msg = "putParam Failed: param: {} val: {}".format(pname, pvalue)
            msg += " Exception: {}".format(e)
            log.error(msg)
        return pversion

    def getParam(self, pn, dcrypt=False):
        """
        retrieves the named parameter
        returns the parameter value or none if an error occured
        see boto3 doc:
            http://boto3.readthedocs.io/en/latest/reference/services/ssm.html#SSM.Client.get_parameter
        """
        pval = None
        bpn = os.path.dirname(pn)
        plist = self.listParameters(bpn)
        if pn in plist:
            try:
                param = self.client.get_parameter(Name=pn, WithDecryption=dcrypt)
                if "Parameter" in param and "Value" in param["Parameter"]:
                    pval = param["Parameter"]["Value"]
            except Exception as e:
                msg = "getParam failed for param: {}".format(pn)
                msg += " Exception was: {}".format(e)
                log.error(msg)
                raise()
        return pval

    def listParameters(self, Path='/'):
        """
        lists all parameters at the level of Path
        returns a list of dicts of parameters at that level
        will recurse down.
        """
        plist = []
        first = True
        nxt = ""
        flts = [{'Key': 'Path', 'Option': 'Recursive', 'Values': [Path, ]}]
        while len(nxt) or first:
            if first:
                first = False
                params = self.client.describe_parameters(ParameterFilters=flts)
            else:
                params = self.client.describe_parameters(ParameterFilters=flts, NextToken=nxt)  # nopep8
            if "NextToken" in params:
                nxt = params["NextToken"]
            else:
                nxt = ""
            for param in params["Parameters"]:
                plist.append(param["Name"])
        return plist

    def getEString(self, pname):
        """
        retrieve an encrypted string parameter
        """
        return self.getParam(pname, True)

    def putEStringParam(self, pname, pvalue, pkeyid=None):
        """
        Store and encrypted string
        """
        return self.putParam(pname, pvalue, 'SecureString', pkeyid)

    def getString(self, pname):
        """
        retrieve a string value
        """
        return self.getParam(pname)

    def putStringParam(self, pname, pvalue):
        """
        Store a string
        """
        return self.putParam(pname, pvalue, 'String')

    def putStringListParam(self, pname, plist):
        """
        Store a list of strings
        """
        return self.putParam(pname, plist, 'StringList')

    def putNumParam(self, pname, pnum):
        """
        Store a numerical value (as a string)
        """
        return self.putParam(pname, pnum, 'String', pattern='^d+$')

    def putENumParam(self, pname, pnum, pkeyid):
        """
        Store a numerical value as an encrypted string
        """
        return self.putParam(pname, pnum, pkeyid=pkeyid, pattern='^d+$')

    def getParams(self, names, environment="prod", path="/sre/chaim/"):
        if not path.endswith("/"):
            path += "/"
        if not environment.endswith("/"):
            environment += "/"
        xpath = path + environment
        log.debug("param path: {}".format(xpath))
        nl = []
        oparams = {}
        for name in names:
            nl.append(xpath + name)
        # log.debug("starting ssm session")
        # sess = boto3.session.Session()
        # log.debug("starting ssm client")
        # client = sess.client("ssm")
        log.debug("asking for {}".format(nl))
        params = self.client.get_parameters(Names=nl, WithDecryption=True)
        if "Parameters" in params:
            prams = params["Parameters"]
            for param in prams:
                name = param["Name"].replace(xpath, '')
                oparams[name] = param["Value"]
        return oparams
