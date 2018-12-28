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
"""filesystem routines"""

import os
import shutil
from pathlib import Path


class FileNotFound(Exception):
    pass


class DirNotFound(Exception):
    pass


class FileSystem(object):
    """filesystem routines implemented as an object"""
    def fileExists(self, fn):
        """returns True if file exists, false otherwise"""
        if len(fn):
            p = Path(fn)
            return p.is_file()
        else:
            return False

    def dirExists(self, dn):
        """returns True if directory exists, false otherwise"""
        d = Path(dn)
        if len(dn):
            return d.is_dir()
        else:
            return False

    def basename(self, fn):
        """returns the basename of the file"""
        return os.path.basename(fn)

    def dirname(self, fn):
        """returns the dirname of the file"""
        return os.path.dirname(fn)

    def makePath(self, pn):
        """makes the full path, including intermediate directories"""
        if not self.dirExists(pn):
            p = Path(pn)
            ret = False
            try:
                p.mkdir(mode=0o755, parents=True, exist_ok=True)
                ret = True
            except Exception as e:
                print("an error occurred making the path {}, exception was {}".format(pn, e))
        else:
            ret = True
        return ret

    def makeFilePath(self, fn):
        """makes the full path for the file."""
        ret = False
        try:
            pfn = self.dirname(fn)
            ret = self.makePath(pfn)
        except Exception as e:
            print("an error occurred making file path {}, exception was {}".format(fn, e))
        return ret

    def absPath(self, fn):
        """returns the absolute path of the file"""
        return os.path.abspath(os.path.expanduser(fn))

    def makeConfigDirs(self, cfg, cfgnames):
        """makes paths from a list"""
        for key in cfgnames:
            self.makePath(cfg[key])

    def rename(self, src, dest):
        """renames the source file"""
        p = Path(src)
        p.rename(dest)

    def copyfile(self, src, dst):
        """copies the file to the fully qualified destination"""
        if self.dirExists(dst):
            dst += "/" + self.basename(src)
        return shutil.copyfile(src, dst)

    def askMe(self, q, default):
        """asks the user a question and returns the answer, or a default answer"""
        ret = default
        val = input("{} ({}) > ".format(q, default))
        if len(val) > 0:
            ret = val
        return ret
