#!/usr/bin/env python3
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
module to install/update lambda code
"""

import argparse
import boto3
import os
import subprocess
import sys
import tempfile
import yaml
# version module is at the top level of this repo (where
# this script lives)
import version
# from chalicelib.filesystem import DirNotFound
# from chalicelib.filesystem import FileNotFound
from chalicelib.filesystem import FileSystem


def getVer():
    return [version.majorv, version.minorv, version.buildv]


def getVerstr():
    xmajorv, xminorv, xbuildv = getVer()
    return str(xmajorv) + '.' + str(xminorv) + '.' + str(xbuildv)


def updateBuild():
    xmajorv, xminorv, xbuildv = getVer()
    xbuildv += 1
    with open(os.path.dirname(__file__) + "/version.py", "w") as vfn:
        vfn.write("majorv = {}\n".format(xmajorv))
        vfn.write("minorv = {}\n".format(xminorv))
        vfn.write("buildv = {}\n".format(xbuildv))
        vfn.write("verstr = str(majorv) + '.' + str(minorv) + '.' + str(buildv)")
    vstr = str(xmajorv) + '.' + str(xminorv) + '.' + str(xbuildv)
    cmd = "git add " + os.path.dirname(__file__) + "/version.py"
    runcmd(cmd)
    with open("version", "w") as vfn:
        vfn.write(vstr)
    cmd = "git add version"
    runcmd(cmd)
    cmsg = "updating chaim to {}".format(vstr)
    print(cmsg)
    cmd = 'git commit -m "' + cmsg + '"'
    runcmd(cmd)
    cmd = 'git push'
    runcmd(cmd)
    return vstr


def runcmd(cmd):
    return subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)


def getFunctions():
    client = boto3.client("lambda")
    funcs = []
    paginate = True
    next = ""
    while paginate:
        if len(next) > 0:
            resp = client.list_functions(Marker=next)
        else:
            resp = client.list_functions()
        for func in resp["Functions"]:
            funcs.append(func)
        if "NextMarker" in resp:
            next = resp["NextMarker"]
        else:
            next = ""
            paginate = False
    return funcs


def findFunction(allfuncs, fnname):
    found = False
    for func in allfuncs:
        if func["FunctionName"] == fnname:
            found = True
            break
    return found


def installRequirements(reqfn, tmpdir):
    fs = FileSystem()
    if fs.fileExists(reqfn):
        cmd = "pip install -r " + reqfn + " -t " + tmpdir
        return runcmd(cmd)
    else:
        print("{} does not exist.".format(reqfn))
        return False


def prepareLambda(fname, vstr, wd, files, reqfn):
    """prepares the zip file for upload to lambda

    wd is the working directory.
    files is a list of files relative to the wd.
    reqfn is the requirements file.

    will make a 'package' directory under the wd
    and place the resulting zip file in it.

    returns the full path to the zip file or False on error.
    """
    ret = False
    fs = FileSystem()
    packd = wd + "/package"
    zipfn = packd + "/" + fname + "-" + vstr + ".zip"
    with tempfile.TemporaryDirectory() as td:
        for fn in files:
            fnd = fs.dirname(fn)
            if len(fnd) > 0:
                tfnd = td + "/" + fnd
                print("looking for dir: {}".format(tfnd))
                if not fs.dirExists(tfnd):
                    print("making dir: {}".format(tfnd))
                    fs.makePath(tfnd)
                fnd += "/"
            dest = td + "/" + fnd + fs.basename(fn)
            print("copying: {} to {}".format(fn, dest))
            xdest = fs.copyfile(fn, dest)
            print("copied {} to {}".format(fn, xdest))
        installRequirements(wd + "/requirements.txt", td)
        fs.makePath(packd)
        os.chdir(td)
        # ensure that the mode of all files in the zip is correct
        print("zipping up")
        cmd = "zip -r " + zipfn + " ."
        runcmd(cmd)
        # pz = PyZip(PyFolder("./", interpret=False))
        # pz.save(zipfn)
        os.chdir(packd)
        ret = True
    return zipfn if ret else None


def updateLambda(lname, config, zipfn, role=None):
    try:
        lc = boto3.client("lambda")
        if lc is not None:
            args = {
                "FunctionName": lname,
                "ZipFile": getZip(zipfn)
            }
            resp = lc.update_function_code(**args)
            if "FunctionArn" in resp:
                print("Updated function {} - arn: {}".format(lname, resp["FunctionArn"]))
            else:
                print("an error occurred updating function, no arn returned")
                sys.exit(1)
            xrole = config["role"] if role is None else role
            tags = unpackList(config["tags"])
            envar = unpackList(config["codeenv"])
            args = {
                "FunctionName": lname,
                "Runtime": config["runtime"],
                "Role": xrole,
                "Handler": config["handler"],
                "Description": config["description"],
                "Timeout": config["timeout"],
                "MemorySize": config["memory"],
                "Environment": {"Variables": envar}
            }
            resp = lc.update_function_configuration(**args)
            if "FunctionArn" in resp:
                print("Updated function config {} - arn: {}".format(lname, resp["FunctionArn"]))
                args = {
                    "Resource": resp["FunctionArn"],
                    "Tags": tags
                }
                lc.tag_resource(**args)
                print("Re-tagged function")
            else:
                print("an error occurred updating function config, no arn returned")
                sys.exit(1)
    except Exception as e:
        emsg = "update lambda: error: {}: {}".format(type(e).__name__, e)
        print(emsg)
        sys.exit(1)


def installLambda(lname, config, zipfn):
    global VPC
    try:
        lc = boto3.client("lambda")
        if lc is not None:
            tags = unpackList(config["tags"])
            envar = unpackList(config["codeenv"])
            args = {
                "FunctionName": lname,
                "Runtime": config["runtime"],
                "Role": config["role"],
                "Handler": config["handler"],
                "Code": {'ZipFile': getZip(zipfn)},
                "Description": config["description"],
                "Timeout": config["timeout"],
                "MemorySize": config["memory"],
                "Publish": True,
                "Environment": {"Variables": envar},
                "Tags": tags
            }
            if VPC:
                vpc = unpackList(config["vpc"])
                args["VpcConfig"] = {
                    'SubnetIds': vpc["subnets"],
                    'SecurityGroupIds': [vpc["securitygroup"]]
                }
            resp = lc.create_function(**args)
            if "FunctionArn" in resp:
                print("Created function {} - arn: {}".format(lname, resp["FunctionArn"]))
            else:
                print("an error occurred, no arn returned")
                sys.exit(1)
        else:
            print("couldn't get a client")
            sys.exit(1)
    except Exception as e:
        emsg = "install lambda: error: {}: {}".format(type(e).__name__, e)
        print(emsg)
        sys.exit(1)


def getZip(zipfn):
    with open(zipfn, 'rb') as zfn:
        bts = zfn.read()
    return bts


def unpackList(carr):
    v = {}
    for ln in carr:
        for k in ln.keys():
            v[k] = ln[k]
    return v


# ------------------
# Script starts here
# ------------------
parser = argparse.ArgumentParser(description="""Installs or updates the lambda functions for chaim.
                                 Designed to be called from make files.""")
parser.add_argument("-b", "--build", action="store_true",
                    help="increment the build number and push to github.")
parser.add_argument("-c", "--clean", action="store_true",
                    help="remove the package/ directories (and their contents) and exit.")
parser.add_argument("-n", "--novpc", action="store_true",
                    help="Do not try and install into a VPC.")
parser.add_argument("environment", default="dev", choices=["dev", "prod", "test"],
                    help="environment to install/update (dev/prod etc).")
args = parser.parse_args()

env = args.environment

medir = os.getcwd()
fs = FileSystem()

VPC = INC = True

if args.clean:
    packd = medir + "/package/"
    if fs.dirExists(packd):
        os.chdir(packd)
        print("cleaning package directory")
        try:
            cmd = "ls -1tr | head -n -1 |xargs rm"
            runcmd(cmd)
        except subprocess.CalledProcessError:
            # ignore errors (if there are no files to clean)
            pass
    sys.exit(0)

if args.novpc:
    VPC = False

if args.build:
    updateBuild()
    sys.exit(0)

me = os.path.basename(medir)
yamlfn = medir + "/" + me + ".yaml"
reqsfn = medir + "/requirements.txt"
if os.path.exists(yamlfn):
    with open(yamlfn, "r") as yfs:
        config = yaml.load(yfs)
    config["tags"][0]["environment"] = env
    config["codeenv"][0]["environment"] = env
    lambdaname = config["tags"][0]["Name"] + "-" + env
    verstr = getVerstr()
    fs.copyfile(os.path.dirname(__file__) + "/version", medir + "/version")
    config["tags"][0]["version"] = verstr
    packd = medir + "/package"
    lzip = packd + "/" + me + "-" + verstr + ".zip"
    if env not in ["dev"] and fs.fileExists(lzip):
        zipfn = lzip
    else:
        zipfn = prepareLambda(me, verstr, medir, config["files"], "requirements.txt")
    if zipfn is None:
        print("failed to create zip file")
        sys.exit(1)
    allfuncs = getFunctions()
    if findFunction(allfuncs, lambdaname):
        print("\nupdating {} to {}\n".format(lambdaname, verstr))
        updateLambda(lambdaname, config, zipfn)
    else:
        print("\nfunction {} doesn't exist, yet, installing {}\n".format(lambdaname, verstr))
        installLambda(lambdaname, config, zipfn)
else:
    print("no config file found: {}".format(yamlfn))
    sys.exit(1)
