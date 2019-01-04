import chaimlib.glue as glue
import chaimlib.chaim as chaim
from chaimlib.envparams import EnvParam
from chaimlib.chaim import SlackRcvFail
from chaimlib.snsclient import SnsClient
from chaimlib.commandparse import CommandParse
from chalice import Chalice


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
        kwargs = {}
        ep = EnvParam()
        kwargs["environment"] = ep.getParam("environment")
        kwargs["useragent"] = "slack"
        kwargs["apiid"] = app.current_request.context["apiId"]
        reqbody = chaim.begin(app.current_request.raw_body.decode(), **kwargs)
        log.debug("request: {}".format(reqbody))
        log.debug("asking for responseurl")
        cp = CommandParse(reqbody, blankbody=True)
        responseurl = cp.responseurl
        log.debug("response url is set to {}".format(responseurl))
        if len(responseurl) == 0 or responseurl is None:
            msg = "no response url in reqbody"
            log.error("{}: {}".format(msg, reqbody))
            raise(SlackRcvFail(msg))
        log.debug("sending to sns: {}".format(reqbody))
        snstopicarn = ep.getParam("SNSTOPIC", decode=True)
        snsc = SnsClient()
        snsc.publishToSns(snstopicarn, reqbody)
        verstr = "chaim-slack-" + kwargs["environment"] + " " + version
        return chaim.output(None, "{}\n\nPlease wait".format(verstr))
    except Exception as e:
        msg = "slackreq: {}: {}".format(type(e).__name__, e)
        log.error(msg)
        return chaim.output(msg)


@app.route('/')
def index():
    return {'hello': 'world'}
