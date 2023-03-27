# -*- coding: utf-8 -*-
# @Time    : 12/20/22 12:37 PM
# @FileName: TTS.py
# @Software: PyCharm
# @Github    ：sudoskys
import asyncio
import base64
import os
import uuid
from pydub import AudioSegment
from pydantic import BaseModel
from Network import NetworkClient


class TTS_REQ(BaseModel):
    model_name: str = ""
    task_id: int = 1
    text: str = "[ZH]你好[ZH]"
    speaker_id: int = 0
    audio_type: str = "ogg"

class TTS_Clint(object):
    @staticmethod
    def decode_audio(encoded_data):
        import base64
        try:
            decoded_data = base64.b64decode(encoded_data)
            return decoded_data
        except Exception as e:
            return None

    @staticmethod
    async def request_vits_server(url: str, params: TTS_REQ):
        """
        接收配置中的参数和构造的数据类，返回字节流
        :param url:
        :param params:
        :return:
        """
        # 发起请求
        try:
            result = await VITS_TTS(url=url).get_speech(params=params)
        except Exception as e:
            print("请求异常1: "+str(e))
            return False, e
        try:
            if isinstance(result, bool):
                return False, "No Api Result"
            if not isinstance(result.get("audio"), str):
                return False, "No Audio Data"
            data = TTS_Clint.decode_audio(result["audio"])
            # 获取当前脚本的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 拼接相对路径
            name = str(uuid.uuid1()) + '.mp3'
            path = os.path.join(current_dir, "Voices")
            tmp_path = path + str(os.path.sep) + name
            print("路径：" + tmp_path)
            #audio_path = os.path.join(current_dir, "voices", "audio.mp3")
            with open(tmp_path, "wb+") as f:
                f.write(data)
            # subprocess.run(["ffmpeg", '-i', tmp_path, '-acodec', 'libopus', audio_path, '-y'])
            # with open(audio_path, 'rb') as f:
            #     data = f.read()
        except Exception as e:
            print("请求异常2: "+str(e))
            return False, e
        else:
            return tmp_path, ""

    @staticmethod
    async def request_vits_server_with_uuid(url: str, params: TTS_REQ, uuid:uuid):
        """
        接收配置中的参数和构造的数据类，返回字节流
        :param url:
        :param params:
        :return:
        """
        # 发起请求
        try:
            result = await VITS_TTS(url=url).get_speech(params=params)
        except Exception as e:
            print("请求异常1: "+str(e))
            return False, e
        try:
            if isinstance(result, bool):
                return False, "No Api Result"
            if not isinstance(result.get("audio"), str):
                return False, "No Audio Data"
            data = TTS_Clint.decode_audio(result["audio"])
            # 获取当前脚本的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 拼接相对路径
            name = str(uuid) + '.mp3'
            path = os.path.join(current_dir, "Voices")
            tmp_path = path + str(os.path.sep) + name
            print("路径：" + tmp_path)
            # combine audio from file
            final_audio = AudioSegment.from_file(tmp_path) if os.path.exists(tmp_path) else None
            # don't know data's detail, write and append manually.
            with open(tmp_path, "wb") as f:
                f.write(data)
            if final_audio:
                final_audio += AudioSegment.from_file(tmp_path)
                final_audio.export(tmp_path, format="mp3")
            # subprocess.run(["ffmpeg", '-i', tmp_path, '-acodec', 'libopus', audio_path, '-y'])
            # with open(audio_path, 'rb') as f:
            #     data = f.read()
        except Exception as e:
            print("请求异常2: "+str(e))
            return False, e
        else:
            return tmp_path, ""


class VITS_TTS(object):
    def __init__(self, url, timeout: int = 600, proxy: str = None):
        self.__url = url
        self.__client = NetworkClient(timeout=timeout, proxy=proxy)

    async def get_speech(self, params: TTS_REQ):
        """
        返回 json
        :param params:
        :return:
        """
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}
        data = params.json()

        response = await self.__client.request(method="POST",
                                               url=self.__url,
                                               data=data,
                                               headers=headers,
                                               )
        print(response)
        if response.status_code != 200:
            print("TTS API Outline")
            return False
        # 接收数据
        response_data = response.json()
        if response_data["code"] != 200:
            print(f"TTS API Error{response_data.get('msg')}")
            return False
        return response_data

# if __name__ == '__main__':
#     params = TTS_REQ(task_id=0,
#                      text="[ZH]你好,我是人工智能.[ZH]",
#                      model_name="1374_epochs.pth",
#                      speaker_id=2,
#                      audio_type="mp3"
#                      )
#
#
#     response = asyncio.run(TTS_Clint().request_vits_server('http://127.0.0.1:9557/tts/generate', params))
#     print(response)
