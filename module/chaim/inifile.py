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
"""Class for reading/writing ini style files"""
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4 foldmethod=indent:
import os
import configparser
import time
from shutil import copyfile
import errno
import threading
import ccalogging

log = ccalogging.log


class IniFile(configparser.ConfigParser):
    """Overidden ConfigParser class to read and write ini format files"""
    def __init__(self, filename, takebackup=True, interpolation=None):
        """Reads filename and parses it into a configparser config structure

        Arguments:
            filename - name of the ini format file to read and parse
        """
        # call the parent constructor
        super().__init__(interpolation=interpolation)
        self.dirty = False
        self.filename = filename
        self.takebackup = takebackup
        self.dir = os.path.dirname(self.filename)
        self.backupdir = "{}/backup".format(self.dir)
        self.backupfn = False
        log.debug("IniFile Class: dir: {}, backup dir: {}".format(self.dir, self.backupdir))
        if not os.path.exists(filename):
            log.error("INI file: {} does not exist".format(self.filename))
            raise FileExistsError("INI file: {} does not exist".format(self.filename))
        self.makeBackup()
        # fp=open(self.filename,"r")
        self.read(self.filename)
        self._lock = threading.Lock()
        # fp.close()

    def makeBackup(self):
        if self.takebackup and self.makeDir(self.backupdir):
            self.backupfn = "{}/{}-{}".format(self.backupdir,
                                              os.path.basename(self.filename),
                                              time.strftime("%Y%m%d%H%M%S"))
            log.debug("backup fn: {}".format(self.backupfn))
            link = "{}/previous-{}".format(self.dir, os.path.basename(self.filename))
            log.debug("previous symlink: {}".format(link))
            copyfile(self.filename, self.backupfn)
            try:
                os.symlink(self.backupfn, link)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    os.remove(link)
                    os.symlink(self.backupfn, link)
                else:
                    raise

    def backupFN(self):
        return self.backupfn

    def makeDir(self, newdir):
        try:
            os.makedirs(newdir)
        except OSError as e:
            # if it exists do nothing
            if e.errno != errno.EEXIST:
                # permissions, disk full etc
                raise
        return True

    def titles(self):
        sectionlist = self.sections()
        return sectionlist

    def sectionExists(self, section):
        ret = False
        titles = self.titles()
        if section in titles:
            ret = True
        return ret

    def getSectionItems(self, section):
        # section items look like
        # [('region', 'eu-west-1'), ('aws_access_key_id', 'xxxxx'), ('aws_secret_access_key', 'xxxxxx')]
        # so, we need to create another dictionary based on the keys
        items = self.items(section)
        k = {}
        for i in range(0, len(items)):
            k[items[i][0]] = items[i][1]
        log.debug("section: {}, items: {}".format(section, items))
        return k

    def updateSection(self, section, datadict, write=False):
        ret = False
        try:
            for k in datadict:
                self.set(section, k, datadict[k])
                log.debug("Setting {} to {} for section {}".format(k, datadict[k], section))
            if write:
                self.saveData()
            ret = True
        except Exception as e:
            log.error("Exception occurred when updating section: {}, {}".format(section, e))
        return ret

    def deleteSection(self, section):
        self.remove_section(section)
        self.saveData()

    def saveData(self):
        with self._lock:
            log.debug("writing out ini file")
            fp = open(self.filename, "w")
            self.write(fp)
            fp.close()
