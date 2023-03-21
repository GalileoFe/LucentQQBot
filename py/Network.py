# -*- coding: utf-8 -*-
# @Time    : 12/20/22 10:51 AM
# @FileName: network.py
# @Software: PyCharm
# @Github    ：sudoskys

from typing import Any
import httpx
#
# import asyncio
# from pydantic import BaseModel
#
#
# class TTS_REQ(BaseModel):
#     model_name: str = ""
#     task_id: int = 1
#     text: str = "[ZH]你好[ZH]"
#     speaker_id: int = 0
#     audio_type: str = "ogg"

class NetworkClient(object):
    def __init__(self, timeout: int = 30, proxy: str = "") -> None:
        proxies = None
        if proxy:
            proxies = {"all://": proxy}
        self.timeout = timeout
        self.proxies = proxies

    async def request(self,
                      method: str,
                      url: str,
                      params: dict = None,
                      data: Any = None,
                      files: Any = None,
                      headers: dict = None,
                      **kwargs
                      ):
        param = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "data": data,
            "headers": headers,
            "files": files,
        }
        param.update(kwargs)
        async with httpx.AsyncClient(timeout=self.timeout, proxies=self.proxies) as client:
            resp = await client.request(**param)
        content_length = resp.headers.get("content-length")
        if content_length and int(content_length) == 0:
            raise Exception("CONTENT LENGTH 0:Server Maybe Not Connected")
        return resp

# if __name__ == "__main__":
#
#     params = TTS_REQ(task_id=0,
#                      text="[ZH]你好,我是人工智能.[ZH]",
#                      model_name="1374_epochs.pth",
#                      speaker_id=2,
#                      audio_type="mp3"
#                      )
#     headers = {'Content-type': 'application/json',
#                'Accept': 'text/plain'}
#     data = params.json()
#     Client = NetworkClient(30)
#     response=asyncio.run(Client.request(method="POST",
#                                                url="http://127.0.0.1:9557/tts/generate",
#                                                data=data,
#                                                headers=headers,
#                                                ))
#     print(response)

