import asyncio

import TTS

"""
参数数量就不改了, 但是这些也没用了, 只需要一个string就行
model name 就是 Moegoe 下后缀为.pth的model名, 记得json config也改成同名的
text记得加[]tag, 不然说不出话.
"""


async def gen_speech(text, voice, path) -> None:
    params = TTS.TTS_REQ(task_id=0,
                     text="[ZH]"+text+"[ZH]",
                     model_name="G_latest.pth",
                     speaker_id=0,
                     audio_type="mp3"
                     )

    tmppath, err = await TTS.TTS_Clint().request_vits_server('http://127.0.0.1:9557/tts/generate', params)
    absPath = str.replace(tmppath, "\\", '//')
    if tmppath:
        absPath = str.replace(tmppath, "\\", "//")
        return absPath
    return err


if __name__ == '__main__':
    path = asyncio.run(gen_speech('你真是有问题啊你这个人.', 'zh-CN-XiaoyiNeural', './voices'))
    print(path)
