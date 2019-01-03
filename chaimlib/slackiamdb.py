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
import pymysql
import chaimlib.glue as glue

log = glue.log


class DBNotConnected(Exception):
    pass


class SlackIamDB():
    def __init__(self, dbhost, dbuser, dbpass, dbdb):
        log.debug("SlackIamDB Entry")
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbdb = dbdb
        self.connected = False
        self.affectedrows = 0
        self.connect()

    def connect(self):
        try:
            self.con = pymysql.connect(self.dbhost, user=self.dbuser,
                                       passwd=self.dbpass, db=self.dbdb)
            log.debug("SlackIamDB connect ok to {}".format(self.dbhost))
            self.connected = True
        except Exception as e:
            msg = "Failed to connect to mysql: {}".format(e)
            log.error(msg)
            self.connected = False
            raise

    def query(self, sql):
        rows = []
        if self.connected:
            try:
                with self.con.cursor() as cur:
                    log.debug("query: {}".format(sql))
                    self.affectedrows = cur.execute(sql)
                    for row in cur:
                        rows.append(row)
            except Exception as e:
                msg = "Failed to execute query: {}.".format(sql)
                msg += ". Exception was: {}".format(e)
                log.error(msg)
                raise
        else:
            msg = "DB Not connected, cannot execute query:{}".format(sql)
            log.error(msg)
            raise(DBNotConnected(msg))
        log.debug("query completed successfully.")
        return rows

    def singleField(self, table, field, where=None):
        sql = "select " + field + " from " + table
        if where is not None:
            sql += " where " + where
        sql += " limit 1"
        rowa = self.query(sql)
        if len(rowa) > 0:
            ret = rowa[0][0]
        else:
            ret = None
        return ret

    def updateQuery(self, sql):
        self.query(sql)
        self.con.commit()
        return self.affectedrows

    def insertQuery(self, sql):
        self.query(sql)
        self.con.commit()
        return self.affectedrows
