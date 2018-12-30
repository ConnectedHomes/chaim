import chaimlib.glue as glue
from chaimlib.wflambda import getWFKey

log = glue.log


def begin(rbody, context, isSlack=False):
    stage = glue.getDefaultValue(context, "stage", "dev")
    if stage == "dev":
        glue.setDebug()
    rbody = glue.addToReqBody(rbody, "stage", stage)
    apiid = glue.getDefaultValue(context, "apiId")
    rbody = glue.addToReqBody(rbody, "apiid", apiid)
    useragent = "slack" if isSlack else glue.getDefaultValue(context, "useragent", "unknown")
    rbody = glue.addToReqBody(rbody, "useragent", useragent)
    getWFKey(stage)
    return rbody
