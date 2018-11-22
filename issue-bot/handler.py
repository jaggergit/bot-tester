import requests, json, os, sys
from github import Github

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

    positive_threshold = os.getenv("positive_threshold", "0,2")

    polarity = res.json()['polarity']

    # Call back to Github to  apply the label.

    apply_label(polarity, 
        payload["issue"]["number"],
        payload["repository"]["full_name"],
        positive_threshold)

    return "Repo: %s, issue: %s, polarity: %f" % (payload["repository"]["full_name"], payload["issue"]["number"], polarity)

def apply_label(polarity, issue_number, repo, positive_threshold):

    sys.stderr.write("->apply_label() polarity: %f issue# %s Repo: %s Threshold: %s \n" % (polarity, issue_number, repo, positive_threshold))
    g = Github(os.getenv("auth_token"))
    repo = g.get_repo(repo)
    issue = repo.get_issue(issue_number)

    has_label_positive = False
    has_label_review = False
    for label in issue.labels:
        if label == "positive":
            has_label_positive = True
        if label == "review":
            has_label_review = True

    if polarity > float(positive_threshold) and not has_label_positive:
        issue.set_labels("positive")
        sys.stderr.write("Setting Positive Labe\n")
    elif not has_label_review:
        issue.set_labels("review")
        sys.stderr.write("Setting Review Labe\n")
