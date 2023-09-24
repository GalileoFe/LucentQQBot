import requests
import json

with open("../config.json", "r") as f:
    config = json.load(f)

MidJourneyServerUrl = config["MidJourneyServerUrl"]["url"]


def submit_imagine_mission(prompt: str, base64Array: list = [], notifyHook: str = "", state: str = ""):
    """
    提交t2i任务
    Args:
        prompt: t2i任务的prompt
    Returns:
        resp: t2i任务的response
    """
    url = MidJourneyServerUrl + "/mj/submit/imagine"
    hearders = {"Content-Type": "application/json"}
    data = {
        "base64Array": [],
        "notifyHook": "",
        "prompt": "Red X",
        "state": ""
    }
    data["prompt"] = prompt
    data["base64Array"] = base64Array
    data["notifyHook"] = notifyHook
    data["state"] = state
    resp = requests.post(url, headers=hearders, data=json.dumps(data))
    return resp
