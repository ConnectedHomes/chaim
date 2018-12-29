#!/usr/bin/env python3
"""
module to install/update lambda code
"""

import boto3
import os
import shutil
import subprocess
import sys
import tempfile
import yaml
from pyzip import PyZip
from pyfolder import PyFolder
# version module is at the top level of this repo (where
# this script lives)
import version
# from chaimlib.filesystem import DirNotFound
# from chaimlib.filesystem import FileNotFound
from chaimlib.filesystem import FileSystem


def getVer():
    return [version.majorv, version.minorv, version.buildv]


def getVerstr():
    xmajorv, xminorv, xbuildv = getVer()
    return str(xmajorv) + '.' + str(xminorv) + '.' + str(xbuildv)


def updateBuild():
    xmajorv, xminorv, xbuildv = getVer()
    with open(os.path.dirname(__file__) + "/version.py", "w") as vfn:
        vfn.write("majorv = {}\n".format(xmajorv))
        vfn.write("minorv = {}\n".format(xminorv))
        vfn.write("buildv = {}\n".format(xbuildv))
        vfn.write("verstr = str(majorv) + '.' + str(minorv) + '.' + str(buildv)")
    return str(xmajorv) + '.' + str(xminorv) + '.' + str(xbuildv)


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
        return subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
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
        subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        # pz = PyZip(PyFolder("./", interpret=False))
        # pz.save(zipfn)
        os.chdir(packd)
        ret = True
    return zipfn if ret else None


def updateLambda(lname, config, zipfn):
    try:
        lc = boto3.client("lambda")
        if lc is not None:
            resp = lc.update_function_code(
                FunctionName=lname,
                ZipFile=getZip(zipfn)
            )
            if "FunctionArn" in resp:
                print("Updated function {} - arn: {}".format(lname, resp["FunctionArn"]))
            else:
                print("an error occurred updating function, no arn returned")
            tags = unpackList(config["tags"])
            envar = unpackList(config["codeenv"])
            resp = lc.update_function_configuration(
                FunctionName=lname,
                Runtime=config["runtime"],
                Role=config["role"],
                Handler=config["handler"],
                Description=config["description"],
                Timeout=config["timeout"],
                MemorySize=config["memory"],
                Environment={"Variables": envar}
            )
            if "FunctionArn" in resp:
                print("Updated function config {} - arn: {}".format(lname, resp["FunctionArn"]))
                lc.tag_resource(Resource=resp["FunctionArn"], Tags=tags)
                print("Re-tagged function")
            else:
                print("an error occurred updating function config, no arn returned")
    except Exception as e:
        emsg = "update lambda: error: {}: {}".format(type(e).__name__, e)
        print(emsg)


def installLambda(lname, config, zipfn):
    try:
        lc = boto3.client("lambda")
        if lc is not None:
            vpc = unpackList(config["vpc"])
            tags = unpackList(config["tags"])
            envar = unpackList(config["codeenv"])
            resp = lc.create_function(
                FunctionName=lname,
                Runtime=config["runtime"],
                Role=config["role"],
                Handler=config["handler"],
                Code={'ZipFile': getZip(zipfn)},
                Description=config["description"],
                Timeout=config["timeout"],
                MemorySize=config["memory"],
                Publish=True,
                VpcConfig={
                    'SubnetIds': vpc["subnets"],
                    'SecurityGroupIds': [vpc["securitygroup"]]
                },
                Environment={"Variables": envar},
                Tags=tags
            )
            if "FunctionArn" in resp:
                print("Created function {} - arn: {}".format(lname, resp["FunctionArn"]))
            else:
                print("an error occurred, no arn returned")
        else:
            print("couldn't get a client")
            sys.exit(1)
    except Exception as e:
        emsg = "install lambda: error: {}: {}".format(type(e).__name__, e)
        print(emsg)


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


env = "dev"
if len(sys.argv) > 1:
    env = sys.argv[1]
medir = os.getcwd()
if env == "-c":
    packd = medir + "/package"
    fs = FileSystem()
    if fs.dirExists(packd):
        shutil.rmtree(packd)
    sys.exit(0)
me = os.path.basename(medir)
yamlfn = medir + "/" + me + ".yaml"
reqsfn = medir + "/requirements.txt"
if os.path.exists(yamlfn):
    with open(yamlfn, "r") as yfs:
        config = yaml.load(yfs)
    config["tags"][0]["environment"] = env
    config["codeenv"][0]["environment"] = env
    verstr = updateBuild() if env in ["dev", "test"] else getVerstr()
    config["tags"][0]["version"] = verstr
    with open("version", "w") as vfn:
        vfn.write(verstr)
    lambdaname = config["tags"][0]["Name"] + "-" + env
    zipfn = prepareLambda(me, verstr, medir, config["files"], "requirements.txt")
    if zipfn is None:
        print("failed to create zip file")
        sys.exit(1)
    allfuncs = getFunctions()
    if findFunction(allfuncs, lambdaname):
        print("lambda {} exists, updating".format(lambdaname))
        updateLambda(lambdaname, config, zipfn)
    else:
        print("function {} doesn't exist, yet, installing".format(lambdaname))
        installLambda(lambdaname, config, zipfn)
else:
    print("no config file found: {}".format(yamlfn))
    sys.exit(1)
