"""
Utilities that don't fit elsewhere
"""
import time
import datetime
import uuid


class Utils():
    def isNumeric(self, xstring):
        try:
            float(xstring)
            return True
        except ValueError:
            return False

    def valMod(self, value, divisor):
        val = int(value / divisor)
        rem = value % divisor
        return [val, rem]

    def hms(self, seconds):
        hrs, rem = self.valMod(seconds, 3600)
        mins, secs = self.valMod(rem, 60)
        return [hrs, mins, secs]

    def dhms(self, seconds):
        dys, rem = self.valMod(seconds, 86400)
        hrs, rem = self.valMod(rem, 3600)
        mins, secs = self.valMod(rem, 60)
        return [dys, hrs, mins, secs]

    def displayWord(self, value, word):
        ret = "{} {}".format(value, word)
        ret += "" if value == 1 else "s"
        return ret

    def hmsDisplay(self, seconds, full=False):
        if seconds > 86400:
            d, h, m, s = self.dhms(seconds)
            dstr = self.displayWord(d, "day")
        else:
            h, m, s = self.hms(seconds)
            dstr = "0 days" if full is True else ""
        hstr = self.displayWord(h, "hour")
        mstr = self.displayWord(m, "minute")
        sstr = self.displayWord(s, "second")
        ret = ""
        if full:
            ret = "{}, {}, {} and {}".format(dstr, hstr, mstr, sstr)
        else:
            if len(dstr):
                ret = "{}, {}, {} and {}".format(dstr, hstr, mstr, sstr)
            else:
                ret = "{}, {} and {}".format(hstr, mstr, sstr)
        return ret

    def expiresInAt(self, seconds, plural=True):
        xstr = "Expires in " if plural else "Expire in "
        xstr += self.hmsDisplay(seconds)
        now = self.getNow()
        then = now + seconds
        whenat = datetime.datetime.fromtimestamp(then).strftime("%H:%M:%S")
        xstr += " at {}.".format(whenat)
        return [then, xstr]

    def expiresAt(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def genUUID(self):
        u = uuid.uuid4()
        return str(u)

    def newUserToken(self, expiredays=30):
        tok = self.genUUID()
        exp = self.getNow()
        exp += int(expiredays * 86400)
        return [tok, int(exp)]

    def newApiToken(self):
        tok = self.genUUID()
        exp = self.getNow()
        exp += 900
        return [tok, int(exp)]

    def getNow(self):
        return int(time.time())
