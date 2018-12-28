#!/usr/bin/env python3
"""
module to install/update lambda code
"""

import os
import sys
import yaml
import boto3
# version module is at the top level of this repo (where
# this script lives)
import version


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


def prepareFunction():
    pass


def updateFunction():
    pass


def installFunction():
    pass


env = "dev"
if len(sys.argv) > 1:
    env = sys.argv[1]
medir = os.getcwd()
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
    allfuncs = getFunctions()
    if findFunction(allfuncs, lambdaname):
        print("er, lambda {} exists".format(lambdaname))
    else:
        print("function {} doesn't exist, yet".format(lambdaname))
else:
    print("no config file found: {}".format(yamlfn))
    sys.exit(1)
