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
from botocore.exceptions import ClientError
import chaimlib.glue as glue

log = glue.log

class NoCreds(Exception):
    pass

class BotoSession():
    """Base class to create a default boto3 session"""
    def __init__(self,theprofile=None,accessid=None,secretkey=None,usedefault=False,stoken=None):
        """sets up a default connection to AWS.

        Either the profile or accessid/secretkey are required
        unless usedefault is set True, whereupon the default, context
        session is created and used, using environment variables if set.

        Keyword Arguments:
            profile - the ~/.aws/credentials profile to use.
            accessid - the aws access key id to use (along with the secret key).
            secretkey - the aws secret access key to use (along with the access key id).
            usedefault - use the default context to create a session.

        Environment Variables:
            AWS_ACCESS_KEY_ID
            AWS_SECRET_ACCESS_KEY
            AWS_SESSION_TOKEN
        """
        self.client=None
        self.profile=None
        self.usekeys=False
        self.usedefault=usedefault
        if self.usedefault==False:
            if theprofile==None and (accessid!=None and secretkey!=None):
                self.accessid=accessid
                self.secretkey=secretkey
                self.stoken=stoken
                self.usekeys=True
            elif theprofile!=None:
                self.profile=theprofile
            else:
                log.error("Required credentials not supplied, cannot continue")
                raise NoCreds("Either the profile or one (or both) keys are missing.")

    def newSession(self):
        if self.profile==None:
            return boto3.session.Session()
        else:
            return boto3.session.Session(profile_name=self.profile)

    def newClient(self,service='iam'):
        try:
            if self.usedefault:
                session=self.newSession()
                self.client=session.client(service)
            elif self.usekeys:
                self.client=boto3.client(service,aws_access_key_id=self.accessid,aws_secret_access_key=self.secretkey,aws_session_token=self.stoken)
            else:
                session=self.newSession()
                self.client=session.client(service)
        except Exception as e:
            log.error("Failed to create a {} client, exception was: {}".format(service,e))
