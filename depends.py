#!/usr/bin/env python3
"""
module to create dependency rules for makefiles
"""
import os
import sys
import yaml

config = None
medir = os.getcwd()
me = os.path.basename(medir)
yamlfn = medir + "/" + me + ".yaml"
reqsfn = medir + "/requirements.txt"
if os.path.exists(yamlfn):
    with open(yamlfn, "r") as yfs:
        config = yaml.load(yfs)
fl = []
if config is not None:
    if "files" in config:
        for fn in config["files"]:
            if fn != "README.md" and fn != "version":
                fl.append(fn)
byamlfn = os.path.basename(yamlfn)
tfn, ext = os.path.splitext(byamlfn)
dyamlfn = tfn + ".d"
if len(fl) > 0:
    xstr = byamlfn + ": " + " ".join(fl)
    with open(medir + "/" + dyamlfn, "w") as dfn:
        dfn.write(xstr + "\n\n")
    sys.exit(0)
sys.exit(1)
