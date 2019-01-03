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
    xstr += " requirements.txt"
    with open(medir + "/" + dyamlfn, "w") as dfn:
        dfn.write(xstr + "\n\n")
    sys.exit(0)
sys.exit(1)
