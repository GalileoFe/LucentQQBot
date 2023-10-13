import requests
import json
from GlobalVariables import respCache
from flask import request, Flask

'''
# 增加一个接口用来回传Mid生成的图片
@MJAPI.route('/get_image', methods=['POST'])
def get_midjourney_image():
    global midjourney_image_url
    global midjourney_image_req_uid
    data = request.get_json()
    image_url = data['imageUrl']
    print('图像已生成')
    print(image_url)
    midjourney_image_url = image_url
    send_private_message_image(
        midjourney_image_req_uid, midjourney_image_url, '')
'''

with open("config.json", "r", encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)

midJourneyServerUrl = config_data["MidJourneyServerUrl"]["url"]
midJourneyNotifyUrl = config_data["MidJourneyServerUrl"]["notifyurl"]
config_port = config_data["qq_bot"]["cqhttp_post_port"] + 1

MJAPI = Flask(__name__)


@MJAPI.route("/get_image", methods=["POST"])
def get_image():
    """
    用于接收MidJourneyServer的回调
    """
    global respCache
    try:
        data = json.loads(request.get_data())
        image_url = data['imageUrl']
        respCache.set()
        respCache.data = image_url
        respCache.clear()
        return "ok"
    except Exception as e:
        return str(e)


def submit_imagine_mission(
        prompt: str,
        base64Array: list = [],
        notifyHook: str = f"{midJourneyNotifyUrl}:{config_port}/get_image",
        state: str = ""):
    """
    提交t2i任务
    Args:
        prompt: t2i任务的prompt
    Returns:
        resp: t2i任务的response
    """
    url = midJourneyServerUrl + "/mj/submit/imagine"
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
    if resp["code"] != 1:
        print(resp["description"])
        return [None, resp]
    else:
        while respCache.is_set() == False:
            pass
        imageUrl = respCache.data
        return [imageUrl, resp]
