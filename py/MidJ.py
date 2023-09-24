import requests
import json
from GlobalVariables import respCache

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

# check if GPT wanted to call a function


def model_call_function(message: str):
'''    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(
            response_message["function_call"]["arguments"])
        function_response = function_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )

        # Step 4: send the info on the function call and function response to GPT
        # extend conversation with assistant's reply
        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response
        '''