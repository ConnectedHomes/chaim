#!/usr/bin/env python3
"""
module to install/update lambda code
"""

import os
import sys
import shutil
import yaml
import boto3
import tempfile
import subprocess
from pyzip import PyZip
from pyfolder import PyFolder
# version module is at the top level of this repo (where
# this script lives)
import version
# from chaimlib.filesystem import DirNotFound
# from chaimlib.filesystem import FileNotFound
from chaimlib.filesystem import FileSystem


def updateBuild():
    xmajorv = version.majorv
    xminorv = version.minorv
    xbuildv = version.buildv + 1
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
        pz = PyZip(PyFolder("./", interpret=False))
        pz.save(zipfn)
        os.chdir(packd)
        ret = True
    return ret


def updateLambda():
    pass


def installLambda():
    pass


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
    config["environment"] = env
    verstr = updateBuild()
    config["version"] = verstr
    with open("version", "w") as vfn:
        vfn.write(verstr)
    lambdaname = config["tags"][0]["Name"] + "-" + env
    prepareLambda(me, verstr, medir, config["files"], "requirements.txt")
    allfuncs = getFunctions()
    if findFunction(allfuncs, lambdaname):
        print("er, lambda {} exists".format(lambdaname))
    else:
        print("function {} doesn't exist, yet".format(lambdaname))
else:
    print("no config file found: {}".format(yamlfn))
    sys.exit(1)
