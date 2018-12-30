from chaimlib.wflambda import getWFKey


def begin(rbody, context, isSlack=False):
    stage = getDefaultValue(context, "stage", "dev")
    if stage == "dev":
        setDebug()
    rbody = addToReqBody(rbody, "stage", stage)
    apiid = getDefaultValue(context, "apiId")
    rbody = addToReqBody(rbody, "apiid", apiid)
    useragent = "slack" if isSlack else getDefaultValue(context, "useragent", "unknown")
    rbody = addToReqBody(rbody, "useragent", useragent)
    getWFKey(stage)
    return rbody
