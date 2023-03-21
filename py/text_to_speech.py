import TTS

"""
参数数量就不改了, 但是这些也没用了, 只需要一个string就行
"""


async def gen_speech(text, voice, path) -> None:
    params = TTS.TTS_REQ(task_id=0,
                     text="[ZH]"+text+"[ZH]",
                     model_name="1374_epochs.pth",
                     speaker_id=2,
                     audio_type="mp3"
                     )

    tmppath,err = await TTS.TTS_Clint().request_vits_server('http://127.0.0.1:9557/tts/generate', params)
    absPath = str.replace(tmppath,"\\",'//')
    return absPath


# if __name__ == '__main__':
#     path = asyncio.run(gen_speech('你真是有问题啊你这个人.', 'zh-CN-XiaoyiNeural', './voices'))
#     print(path)
