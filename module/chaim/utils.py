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
Utilities that don't fit elsewhere
"""
import time
import datetime
import uuid


def isNumeric(xstring):
    try:
        float(xstring)
        return True
    except ValueError:
        return False


def valMod(value, divisor):
    val = int(value / divisor)
    rem = value % divisor
    return [val, rem]


def hms(seconds):
    hrs, rem = valMod(seconds, 3600)
    mins, secs = valMod(rem, 60)
    return [hrs, mins, secs]


def dhms(seconds):
    dys, rem = valMod(seconds, 86400)
    hrs, rem = valMod(rem, 3600)
    mins, secs = valMod(rem, 60)
    return [dys, hrs, mins, secs]


def displayWord(value, word):
    ret = "{} {}".format(value, word)
    ret += "" if value == 1 else "s"
    return ret


def hmsDisplay(seconds, full=False):
    if seconds > 86400:
        d, h, m, s = dhms(seconds)
        dstr = displayWord(d, "day")
    else:
        h, m, s = hms(seconds)
        dstr = "0 days" if full is True else ""
    hstr = displayWord(h, "hour")
    mstr = displayWord(m, "minute")
    sstr = displayWord(s, "second")
    ret = ""
    if full:
        ret = "{}, {}, {} and {}".format(dstr, hstr, mstr, sstr)
    else:
        if len(dstr):
            ret = "{}, {}, {} and {}".format(dstr, hstr, mstr, sstr)
        else:
            ret = "{}, {} and {}".format(hstr, mstr, sstr)
    return ret

def displayHMS(seconds, fuzzy=True):
    xstr = ""
    d, h, m, s = dhms(seconds)
    if fuzzy:
        if d > 0:
            if h > 12:
                d = d + 1
            xstr = displayWord(d, "day")
        elif h > 0:
            if m > 30:
                h = h + 1
            xstr = displayWord(h, "hour")
        elif m > 0:
            if s > 30:
                m = m + 1
            xstr = displayWord(m, "minute")
        else:
            xstr = displayWord(s, "second")
    else:
        xstr = displayWord(d, "day")
        xstr += ", " + displayWord(h, "hour")
        xstr += ", " + displayWord(m, "minute")
        xstr += " and " + displayWord(s, "second")
    return xstr


# def expiresInAt(seconds):
#     xstr = "Expires in "
#     xstr += hmsDisplay(seconds)
#     now = getNow()
#     then = now + seconds
#     whenat = datetime.datetime.fromtimestamp(then).strftime("%H:%M:%S")
#     xstr += " at {}.".format(whenat)
#     return [then, xstr]
def expiresInAt(seconds, plural=True):
    xstr = "Expires in " if plural else "Expire in "
    xstr += displayHMS(seconds)
    now = getNow()
    then = now + seconds
    whenat = datetime.datetime.fromtimestamp(then).strftime("%H:%M:%S")
    xstr += " at {}.".format(whenat)
    return [then, xstr]



def displayExpires(expires, duration=None):
    now = getNow()
    if expires < now:
        return "has expired."
    else:
        then, xstr = expiresInAt(expires - now)
        if duration is not None:
            pc = expiresPercentRemaining(duration, expires)
            xstr += " [{}%]".format(pc)
        return xstr


def genUUID():
    u = uuid.uuid4()
    return str(u)


def newUserToken(expiredays=30):
    tok = genUUID()
    exp = getNow()
    exp += int(expiredays * 86400)
    return [tok, int(exp)]


def newApiToken():
    tok = genUUID()
    exp = getNow()
    exp += 900
    return [tok, int(exp)]


def getNow():
    return int(time.time())


def coerceDuration(duration):
    if duration < 13:
        xd = duration * 3600
    else:
        xd = duration
    if xd > 43200:
        xd = 43200
    if xd < 900:
        xd = 900
    return xd


def expiresPercentRemaining(duration, expires):
    xd = coerceDuration(duration)
    now = getNow()
    # check to see if the credentials have already expired
    if expires < now:
        return 0
    left = expires - now
    # if less than 20 minutes left you'll probably not get a valid url
    if left < 1200:
        return 1
    pc = int((float(left) / float(xd)) * 100)
    return pc
