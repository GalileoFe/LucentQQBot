import requests
import json
from GlobalVariables import respCache

with open("config.json", "r", encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)

MidJourneyServerUrl = config_data["MidJourneyServerUrl"]["url"]
config_port = config_data["qq_bot"]["cqhttp_post_port"]


def submit_imagine_mission(
    prompt: str, 
    base64Array: list = [], 
    notifyHook: str = f"http://0.0.0.0:{config_port}/get_image", 
    state: str = ""):
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
