import sys


class TestException(Exception):
    pass



def formatMsg(fname, e):
    return "Error in {}: Exception: {}: {}\n".format(fname, type(e).__name__, e)


def errorExit(fname, e, exitlevel=1):
    msg = formatMsg(fname, e)
    sys.stderr.write(msg)
    # sys.stderr.flush()
    sys.exit(exitlevel)


def errorRaise(fname, e):
    msg = formatMsg(fname, e)
    sys.stderr.write(msg)
    raise(e)


def errorNotify(fname, e):
    msg = formatMsg(fname, e)
    sys.stderr.write(msg)
    if fname == "testErrorNotify":
        return msg


def template():
    try:
        pass
    except TestException as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)
