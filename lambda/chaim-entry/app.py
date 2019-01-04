import chaimlib.glue as glue
import chaimlib.chaim as chaim
from chaimlib.envparams import EnvParam
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


@app.route('/')
def index():
    return {'hello': 'world'}
