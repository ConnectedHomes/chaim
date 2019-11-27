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
"""Logging for chaim"""
import sys
import logging

# logging.basicConfig(format="%(asctime)s [%(levelname)-5.5s] %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
log = logging.getLogger("chaim")
# setConsoleOut()
# setInfo()

def setDebug():
    log.setLevel(logging.DEBUG)

def setInfo():
    log.setLevel(logging.INFO)

def setWarn():
    log.setLevel(logging.WARNING)

def setError():
    log.setLevel(logging.ERROR)

def setLogFile(fqfn, fformat="%(asctime)s [%(levelname)-5.5s]  %(message)s", datefmt="%d/%m/%Y %H:%M:%S"):
    """
    sets log output to go to a file
    """
    ffmt = logging.Formatter(fformat, datefmt=datefmt)
    fileH = logging.FileHandler(fqfn)
    fileH.setFormatter(ffmt)
    log.addHandler(fileH)

def setConsoleOut(STDOUT=False, cformat="%(asctime)s [%(levelname)-5.5s]  %(message)s", datefmt="%d/%m/%Y %H:%M:%S"):
    """
    sets log output to goto the console (stderr by default)
    """
    cfmt = logging.Formatter(cformat, datefmt=datefmt)
    if STDOUT:
        consH = logging.StreamHandler(sys.stdout)
    else:
        consH = logging.StreamHandler(sys.stderr)
    consH.setFormatter(cfmt)
    log.addHandler(consH)
