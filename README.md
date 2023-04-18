# LucentQQBot
 Customized QQBot originally made by @Lucent, edited by @Tasse, @空白. Last modified by me. now suports Claude in Slack

 
# QQ 机器人 🤖
这是一个 QQ 机器人，它可以执行各种有趣的操作，包括语音合成和预设加载,分段发送回复以及人格关系。


# 🎉 更新日志 - 版本2.3 🚀
在版本2.3的更新中，我们带来了一项令人兴奋的新功能：Claude on Slack的支持！🥳 这将让你们更轻松地与Claude互动并享受更多乐趣！以下是更新内容的简要概述：

## 🌟 新增Claude in Slack的支持:
现在，您可以在QQ上与Claude in Slack愉快地打交道！🤖 只需查阅Slack_Bot.py文件中的注释，详细了解如何使用与Claude in Slack对话的新方式，并开始轻松愉快的聊天体验。
## 🎯 更出色的角色扮演功能：
Claude的角色扮演能力十分出色，让您在与Claude in Slack互动时更加投入和难以忘怀。😎 共同开展激动人心的角色扮演冒险。
## 💬 兼容原始的对话模式：
为了让您的体验更加完美，我们已兼容了原始的对话模式。💪 无论您喜欢使用群聊共享还是群聊独立的会话模式，新的Claude都能支持，为您带来愉快的互动体验。

## 🔍 使用前千万不要忘记查看 **[Claude 使用须知](https://github.com/BlackPinkiller/LucentQQBot/blob/main/Claude教程（必读！）.pdf)** ！
 这是非常重要的一步，能让您充分掌握所有必要信息，避免遇到困难！😮🚨✅ 帮助文件来自 @云端 倾情撰写

以上仅是本次更新中的部分内容。💫 具体过往内容请前往更新日志查看 🙌 <br>如果您对本次更新的其他功能或信息感兴趣，请随时向我们提问。我们会竭诚为您提供更多帮助！感谢您支持和使用！🎯

# 预设加载 📃
该机器人可以通过热加载 txt 文件，将其作为预设加载到机器人中。只需将预设文件放入根目录下的 presets 文件夹中，通过" **指令列表** " **重新加载配置文件** 热更新, 更多设置同样通过" **指令列表** "来查看

# Vits 语音 🎤
该机器人还包含了 **[@Moegoe](https://github.com/LlmKira/MoeGoe) Vits** 语音功能。只需在消息中提及机器人并使用关键词"语音回复"(**需先配置并运行Moegoe Server ( **有些难度** )**)，即可启用语音功能。该机器人使用的 Vits 模型可以根据需要进行自定义。

发送qq语音需要用到[FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases)并配置\bin目录到系统环境变量path里.<br>否则只会发送语音的本地地址.

# 默认Vits Model
## Chinese & Japanese
Nene + Nanami + Rong + Tang<br>默认speaker = 2 (小茸)
可以在text_to_speech里修改
model_name=""
speaker_id=0
不要忘记在MoeGoe\model\index.json里加上你的模型.

Download [Config File](https://sjtueducn-my.sharepoint.com/:u:/g/personal/cjang_cjengh_sjtu_edu_cn/EYZfZuW5jtxIqIesYOpFuB4BVWtItUIO2f9YxGQZelRxaQ?e=MCZPCL)

Download [Model](https://sjtueducn-my.sharepoint.com/:u:/g/personal/cjang_cjengh_sjtu_edu_cn/EQ0IKHchgzZAt0E6GryW17EBsIlIkmby6BcO9FtoODjwNQ?e=5uzWtj) (1374 epochs)


# 使用方法 🛠️
克隆本仓库

将预设文件添加到 presets 文件夹中

在根目录下 Config 文件中，修改 API 和指定机器人的 QQ 号。例如：

"api_key": ["123456"] # 可多个, 用","分隔, 不要使用中文标点哦。

"qq_no": "1234567890" # 机器人QQ号码。

<br><br>有些设置是我没删掉但没效果的, 填了没有影响
比如"voice","voice_path"。

# 问题和反馈 🤔
一些内容在 **[部分说明](https://github.com/BlackPinkiller/LucentQQBot/blob/main/%E9%83%A8%E5%88%86%E8%AF%B4%E6%98%8E(%E7%9C%8B%E8%BF%99%E4%B8%AA).pdf)** 里有涵盖, 可以先浅看一下.
如果您在使用机器人时遇到任何问题，请随时提交 Issue 或向我们发送反馈。我们会尽快回复并尽力解决您的问题。

谢谢您的使用！ 😊




<br><br>本介绍由Chat GPT倾情赞助。
