import asyncio
from langCodeDetectSlow import detect_language_with_prefix_code_multi_sentence as detect
import TTS
"""
    参数数量就不改了, 但是这些也没用了, 只需要一个string就行
    model name 就是 Moegoe 下后缀为.pth的model名, 记得json config也改成同名的
    langCodeDetectFast是比较快的识别api, 但是准确度有些堪忧, 有些时候会把中文识别成韩文
    langCodeDetectSlow会慢三四倍, 但是准确度很高, 看取舍.
    但是和语音生成的速度比的话, 两三秒差距就不大了.
    如果要替换的话直接用langCodeDetectSlow替换上面的langCodeDetectFast, 
    名称方法都是完全通用的, 不需要任何改变.
"""


async def gen_speech(text, voice, path) -> None:
    index = 0
    multilineText = detect(text)
    import uuid
    uid = uuid.uuid1()
    while index < len(multilineText):
        params = TTS.TTS_REQ(task_id=0,
                             text=multilineText[index],
                             model_name="1374_epochs.pth",
                             speaker_id=2,
                             audio_type="ogg"
                             )
        try:
            tmppath, err = await TTS.TTS_Clint().request_vits_server_with_uuid('http://127.0.0.1:9557/tts/generate', params, uid)
            if tmppath and index == len(multilineText)-1:
                absPath = str.replace(tmppath, "\\", "//")
                return absPath
            index += 1
        except Exception as e:
            print("exception: " + e + "error: " + err)
    return err

# 测试而已
# if __name__ == '__main__':
#     text = "我的邮箱是:blackink@mail.com. http://www.example.com/path/to/file.html. what can I help you with.[今天天气很好.]Bonjour, je m’appelle Celia.Hello! How are you? I'm doing fine, thank you! 今日はいい天気ですね。你好."#
#     path = asyncio.run(gen_speech(text, 'zh-CN-XiaoyiNeural', './voices'))
#
#     path = asyncio.run(gen_speech('今天天气很好.]][很适合出去玩呢.] 今日はいい天気ですね。', 'zh-CN-XiaoyiNeural', './voices'))
#     print(path)
