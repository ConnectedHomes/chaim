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
"""Base Module for creating a default session with boto3 to AWS"""
import boto3
import chalicelib.glue as glue

log = glue.log


class NoCreds(Exception):
    pass


class BotoSession():
    """Base class to create a default boto3 session"""
    def __init__(self, **kwargs):
        """sets up a default connection to AWS.

        will use the default setting from your credentials file unless
        either the profile or accessid/secretkey are supplied.

        Keyword Arguments:
            profile - the ~/.aws/credentials profile to use.
            accesskey - the aws access key id to use (along with the secret key).
            secretkey - the aws secret access key to use (along with the access key id).
            stoken - the aws session token to use

        Environment Variables (if set override the default credentials):
            AWS_ACCESS_KEY_ID
            AWS_SECRET_ACCESS_KEY
            AWS_SESSION_TOKEN
        """
        self.client = None
        self.profile = None
        self.usekeys = False
        self.kwargs = None
        self.usedefault = True
        if len(kwargs) > 0:
            if "profile" in kwargs:
                self.profile = kwargs["profile"]
            elif "accesskey" in kwargs and "secretkey" in kwargs:
                self.kwargs = {}
                self.kwargs["aws_access_key_id"] = kwargs["accesskey"]
                self.kwargs["aws_secret_access_key"] = kwargs["secretkey"]
                if "stoken" in kwargs:
                    self.kwargs["aws_session_token"] = kwargs["stoken"]
                self.usekeys = True
                self.usedefault = False
            else:
                emsg = "Incomplete credentials supplied"
                raise NoCreds(emsg)

    def newSession(self):
        if self.profile is None:
            return boto3.session.Session()
        else:
            return boto3.session.Session(profile_name=self.profile)

    def newClient(self, service='iam'):
        try:
            if self.usekeys:
                self.client = boto3.client(service, **self.kwargs)
            else:
                session = self.newSession()
                self.client = session.client(service)
        except Exception as e:
            msg = "Failed to create a {} client. {}: {}".format(service, type(e).__name__, e)
            log.error(msg)
            raise NoCreds(msg)
        return self.client
