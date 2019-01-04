from chaimlib.commandparse import CommandParse
from chaimlib.envparams import EnvParam
from chaimlib.permissions import DataNotFound
from chaimlib.permissions import Permissions
from chaimlib.wflambda import wfwrapper
from chalice import Chalice
import chaimlib.chaim as chaim
import chaimlib.glue as glue


log = glue.log


app = Chalice(app_name='chaim-entry')


@app.route('/slackreq', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def slackreq():
    """
    This is the entry point for Slack
    """
    try:
        with open("version", "r") as vfn:
            version = vfn.read()
        config = {}
        ep = EnvParam()
        config["environment"] = ep.getParam("environment")
        config["useragent"] = "slack"
        config["apiid"] = app.current_request.context["apiId"]
        chaim.snsPublish(ep.getParam("SNSTOPIC"),
                         chaim.begin(app.current_request.raw_body.decode(), **config))
        verstr = "chaim-slack-" + config["environment"] + " " + version
        return chaim.output(None, "{}\n\nPlease wait".format(verstr))
    except Exception as e:
        emsg = "slackreq: {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        return chaim.output(emsg)


@wfwrapper
def doStart(reqbody, env, version):
    try:
        verstr = "chaim-cli-{}".format(env) + " " + version
        log.debug("{} doStart entered: {}".format(verstr, reqbody))
        ep = EnvParam()
        secretpath = ep.getParam("SECRETPATH")
        pms = Permissions(secretpath, stagepath=env + "/")
        cp = CommandParse(reqbody, roledict=pms.roleAliasDict())
        emsg = ""
        if cp.dolist:
            log.debug("cli account list request")
            kdict = {"accountlist": pms.accountList()}
        else:
            rdict = cp.requestDict()
            msg = "incoming CLI request: user agent"
            msg += " unknown!" if rdict["useragent"] is None else " {}".format(rdict["useragent"])
            log.info(msg)
            if "role" in rdict:
                if rdict["role"] is None:
                    raise DataNotFound("Role not recognised: {}".format(rdict["rolealias"]))
            log.debug("incoming cli request: {}".format(rdict))
            kdict, rdict = chaim.buildCredentials(pms, rdict, noUrl=True)
            if kdict is None:
                emsg = "Failed to build credentials"
            else:
                chaim.incMetric("key.cli")
        return [emsg, kdict]
    except Exception as e:
        emsg = "doStart: Error {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        chaim.incMetric("key.cli.error")
        return [emsg, None]


@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def start():
    """
    The entry point for the CLI
    """
    try:
        config = {}
        ep = EnvParam()
        config["environment"] = ep.getParam("environment")
        rbody = chaim.begin(app.current_request.raw_body.decode(), **config)
        with open("version", "r") as vfn:
            version = vfn.read()
        emsg, msg = doStart(rbody, config["environment"], version)
        return chaim.output(emsg, msg)
    except Exception as e:
        emsg = "cli start: {}: {}".format(type(e).__name__, e)
        log.error(emsg)
        return chaim.output(emsg)
