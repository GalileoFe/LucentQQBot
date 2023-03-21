# LucentQQBot
 Customized QQBot originally made by @Lucent, edited by @Tasse. Last modified by me.
 
 
 
# QQ 机器人 🤖
这是一个 QQ 机器人，它可以执行各种有趣的操作，包括语音合成和预设加载。

# 预设加载 📃
该机器人可以通过热加载 txt 文件，将其作为预设加载到机器人中。只需将预设文件放入根目录下的 presets 文件夹中，机器人将自动加载预设文件。如果在预设文件更改时，机器人会自动重新加载文件。

请注意，由于当前代码中没有多余的判断，如果预设文件非常多，可能会影响机器人的性能。

# Vits 语音 🎤
该机器人还包含了 [@Moegoe](https://github.com/LlmKira/MoeGoe) Vits 语音功能。只需在消息中提及机器人并使用关键词"语音开启"，即可启用语音功能。该机器人使用的 Vits 模型可以根据需要进行自定义。

# 默认Vits Model
## Chinese & Japanese
Nene + Nanami + Rong + Tang<br>默认speaker = 2 (小茸)

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
如果您在使用机器人时遇到任何问题，请随时提交 Issue 或向我们发送反馈。我们会尽快回复并尽力解决您的问题。

谢谢您的使用！ 😊




<br><br>本介绍由Chat GPT倾情赞助。
