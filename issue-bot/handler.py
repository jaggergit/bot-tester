import requests, json, os, sys

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    event_header = os.getenv("Http_X_Github_Event")
    req_user_agent = os.getenv("Http_User_Agent")

    sys.stderr.write("User Agent: " + req_user_agent + "\n")

    if not event_header == "issues":
        sys.exit("Unexpected X-GitHub-Event: " + event_header)
    
    gateway_hostname = os.getenv("gateway_hostname", "gateway")
#Converts JSON to Python objects
    payload = json.loads(req)
    
    if not payload["action"] == "opened":
        sys.stderr.write("payload action != open .. exiting \n")
        return

#sentimentanalysis invokation

    res = requests.post('http://' + gateway_hostname + ':8080/function/sentimentanalysis', data=payload["issue"]["title"]+" "+payload["issue"]["body"])

    sys.stderr.write("post call to sentimentanalysis - return code: " + str(res.status_code) + "\n")
    
    if not res.status_code == 200:
        sys.exit("Error from sentimentanalysis")

    sys.stderr.write("Json Response to Sever:\n" + str(res.json()) + "\n")
    return res.json()
