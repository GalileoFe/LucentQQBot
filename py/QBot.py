import json
import os
import traceback
import uuid
from copy import deepcopy
from flask import request, Flask
import openai
import requests
from CustomDic import CustomDict
from text_to_image import text_to_image
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import tiktoken
from text_to_speech import gen_speech
import asyncio
import adv # 导入adv.py
import banlist # 导入banlist.py
from txtReader import read_txt_files

global config_data
with open("config.json", "r",
          encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)
    qq_no = config_data['qq_bot']['qq_no']

# 注：安全人格即用户在无权限（权限指是否位于advanced_users组中）时只能使用的人格，若您不需要限制，请把此值设为默认人格的序号
safe_preset = 0 # 安全人格（序号与人格简述的序号对应）

# 管理员QQ(可以添加权限和切换群聊对话模式，可设置多个)
moderator_qq = ["632714787"]

# 注：安全模式即用户在无权限时无法使用自定义人格，若您不需要限制，请把此值设为False
safe_mode = False# 安全模式

# 热加载, 监听characters, 会在字典被读取的时候重载presets目录, 并删去旧字典中未被覆盖到的过长的预设
# 举例:presets目录下有5个预设, 删掉一个之后变成4个, 需要去掉第五个不然会导致问题


def Characterlistener():
    txtKeys = read_txt_files()
    if len(character_description) - 2 > len(txtKeys):
        toremove = []
        for k, v in character_description.items():
            if not int(str(k)) <= 0 and k not in txtKeys.keys():
                toremove.append(k)
        for k in toremove:
            del character_description[k]
    for i, key in enumerate(txtKeys.keys()):
        character_description[i + 1] = key
        config_data['chatgpt']['preset'+str(i+1)] = txtKeys[key]


# 人格简述（序号X要与config.json中的"presetX"对应）
# 例如：config.json中"preset0"对应的序号就为0
# 注意：此处的简述为人格列表展示和人格切换用！此处不应填写详细人设，详细人设应填写于config.json
initialData = {
    -1:'自定义',  # '自定义'别改
    0:'默认人设（孙吧嘴臭人）',
    1:'Aoi(病娇少女)',
    2:'音音',
    3:'人设3号'
}

character_description = CustomDict(initialData, listener=Characterlistener)


if safe_mode: # 若安全模式
    session_config = {
        'msg': [
            {"role": "system", "content": config_data['chatgpt']['preset'+str(safe_preset)]} # 对话初始人格为安全人格
        ],
        "character": safe_preset,
        'send_voice': False
    }
else:
    session_config = {
        'msg': [
            {"role": "system", "content": config_data['chatgpt']['preset0']} # 对话初始人格为默认人格
        ],
        "character": 0,
        'send_voice': False
    }

advanced_users = adv.advanced_users # 导入adv.py中的列表数据

# 导入banlist中的数据
ban_person = banlist.ban_person
ban_group = banlist.ban_group

# 正在使用群聊共享对话的群组
general_enabled_group = []

sessions = {}
current_key_index = 0

openai.api_base = "https://chat-gpt.aurorax.cloud/v1"

# 创建一个服务，把当前这个python文件当做一个服务
server = Flask(__name__)


# 测试接口，可以测试本代码是否正常启动
@server.route('/', methods=["GET"])
def index():
    return f"你好，世界!<br/>"


# 获取账号余额接口
@server.route('/credit_summary', methods=["GET"])
def credit_summary():
    return get_credit_summary()


# qq消息上报接口，qq机器人监听到的消息内容将被上报到这里
@server.route('/', methods=["POST"])
def get_message():
    if request.get_json().get('message_type') == 'private':  # 如果是私聊信息
        uid = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ号码
        message = request.get_json().get('raw_message')  # 获取原始信息
        sender = request.get_json().get('sender')  # 消息发送者的资料
        print("收到私聊消息：")
        print(message)
        # 下面你可以执行更多逻辑，这里只演示与ChatGPT对话
        if message.strip().startswith('生成图像'):
            message = str(message).replace('生成图像', '')
            session = get_chat_session('P' + str(uid))
            msg_text = chat(message, session)  # 将消息转发给ChatGPT处理
            # 将ChatGPT的描述转换为图画
            print('开始生成图像')
            pic_path = get_openai_image(msg_text)
            send_private_message_image(uid, pic_path, msg_text)
        elif message.strip().startswith('直接生成图像'):
            message = str(message).replace('直接生成图像', '')
            print('开始直接生成图像')
            pic_path = get_openai_image(message)
            send_private_message_image(uid, pic_path, '')
        else:
            # 获得对话session
            session = get_chat_session('P' + str(uid))
            msg_text = chat(message, 'P' + str(uid))  # 将消息转发给ChatGPT处理
            send_private_message(uid, msg_text, session['send_voice'])  # 将消息返回的内容发送给用户

    if request.get_json().get('message_type') == 'group':  # 如果是群消息
       gid = request.get_json().get('group_id')  # 群号
       uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
       message = request.get_json().get('raw_message')  # 获取原始信息
       # 判断当被@或触发关键词时才回答
       if str("[CQ:at,qq=%s]" % qq_no) in message:
           sender = request.get_json().get('sender')  # 消息发送者的资料
           print("收到群聊消息：")
           print(request.get_json().get('sender').get('nickname'))
           print(message)
           message = str(message).replace(str("[CQ:at,qq=%s]" % qq_no), '')
           if (str("戳一戳[CQ:at") in message): # 判断是否为戳一戳请求
               poke_request = True
           else:
               poke_request = False
           if message.strip().startswith('生成图像'):
               message = str(message).replace('生成图像', '')
               msg_text = chat(message, 'G' + str(gid))  # 将消息转发给ChatGPT处理
               # 将ChatGPT的描述转换为图画
               print('开始生成图像')
               pic_path = get_openai_image(msg_text)
               send_group_message_image(gid, pic_path, uid, msg_text)
           elif message.strip().startswith('直接生成图像'):
               message = str(message).replace('直接生成图像', '')
               print('开始直接生成图像')
               pic_path = get_openai_image(message)
               send_group_message_image(gid, pic_path, uid, '')
           else:
               # 戳一戳
               if poke_request:
                   message = re.sub(r"(.*)\[CQ:at, qq=(\d+)\]", '', message)
                   msg_text = str(message).replace(str("[CQ:at"), str("[CQ:poke"))
               else:
                   global general_chat
                   # 下面你可以执行更多逻辑，这里只演示与ChatGPT对话
                   # 判断对话模式
                   if (str(gid) in general_enabled_group):
                       session = get_chat_session('P' + str(uid))
                       msg_text = chat(message, 'P' + str(gid))  # 将消息转发给ChatGPT处理（群聊共享对话）
                   else:
                       session = get_chat_session('G' + str(uid))
                       msg_text = chat(message, 'G' + str(uid))  # 将消息转发给ChatGPT处理（个人独立对话）

               send_group_message(gid, msg_text, uid, session['send_voice'])  # 将消息转发到群里

    if request.get_json().get('post_type') == 'request':  # 收到请求消息
        print("收到请求消息")
        request_type = request.get_json().get('request_type')  # group
        uid = request.get_json().get('user_id')
        flag = request.get_json().get('flag')
        comment = request.get_json().get('comment')
        print("配置文件 auto_confirm:" + str(config_data['qq_bot']['auto_confirm']) + " admin_qq: " + str(
            config_data['qq_bot']['admin_qq']))
        if request_type == "friend":
            print("收到加好友申请")
            print("QQ：", uid)
            print("验证信息", comment)
            # 如果配置文件里auto_confirm为 TRUE，则自动通过
            if config_data['qq_bot']['auto_confirm']:
                set_friend_add_request(flag, "true")
            else:
                if str(uid) == config_data['qq_bot']['admin_qq']:  # 否则只有管理员的好友请求会通过
                    print("管理员加好友请求，通过")
                    set_friend_add_request(flag, "true")
        if request_type == "group":
            print("收到群请求")
            sub_type = request.get_json().get('sub_type')  # 两种，一种的加群(当机器人为管理员的情况下)，一种是邀请入群
            gid = request.get_json().get('group_id')
            if sub_type == "add":
                # 如果机器人是管理员，会收到这种请求，请自行处理
                print("收到加群申请，不进行处理")
            elif sub_type == "invite":
                print("收到邀请入群申请")
                print("群号：", gid)
                # 如果配置文件里auto_confirm为 TRUE，则自动通过
                if config_data['qq_bot']['auto_confirm']:
                    set_group_invite_request(flag, "true")
                else:
                    if str(uid) == config_data['qq_bot']['admin_qq']:  # 否则只有管理员的拉群请求会通过
                        set_group_invite_request(flag, "true")
    return "ok"


# 测试接口，可以用来测试与ChatGPT的交互是否正常，用来排查问题
@server.route('/chat', methods=['post'])
def chatapi():
    requestJson = request.get_data()
    if requestJson is None or requestJson == "" or requestJson == {}:
        resu = {'code': 1, 'msg': '请求内容不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    data = json.loads(requestJson)
    if data.get('id') is None or data['id'] == "":
        resu = {'code': 1, 'msg': '会话id不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    print(data)
    try:
        s = get_chat_session(data['id'])
        msg = chat(data['msg'], s)
        if '查询余额' == data['msg'].strip():
            msg = msg.replace('\n', '<br/>')
        resu = {'code': 0, 'data': msg, 'id': data['id']}
        return json.dumps(resu, ensure_ascii=False)
    except Exception as error:
        print("接口报错")
        resu = {'code': 1, 'msg': '请求异常: ' + str(error)}
        return json.dumps(resu, ensure_ascii=False)


# 重置会话接口
@server.route('/reset_chat', methods=['post'])
def reset_chat():
    requestJson = request.get_data()
    if requestJson is None or requestJson == "" or requestJson == {}:
        resu = {'code': 1, 'msg': '请求内容不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    data = json.loads(requestJson)
    if data['id'] is None or data['id'] == "":
        resu = {'code': 1, 'msg': '会话id不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    # 获得对话session
    session = get_chat_session(data['id'])
    # 清除对话内容但保留人设
    del session['msg'][1:len(session['msg'])]
    resu = {'code': 0, 'msg': '重置成功'}
    return json.dumps(resu, ensure_ascii=False)


# 与ChatGPT交互的方法
def chat(msg, sessionid):
    try:
        global advanced_users
        global safe_mode
        if msg.strip() == '':
            return '您好，我是人工智能助手，如果您有任何问题，请随时告诉我，我将尽力回答。\n如果您需要重置我们的会话，请回复`重置会话`'
        # 获得对话session
        session = get_chat_session(sessionid)
        if '语音开启' == msg.strip():
            session['send_voice'] = True
            return '语音回复已开启'
        if '语音关闭' == msg.strip():
            session['send_voice'] = False
            return '语音回复已关闭'
        if '重置会话' == msg.strip():
            # 清除对话内容但保留人设
            del session['msg'][1:len(session['msg'])]
            return "会话已重置"
        if '重置人格' == msg.strip():
            uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
            if ((str(uid) in (advanced_users or moderator_qq)) or (safe_mode == False)):  # 若用户在advanced_users组中或安全模式关
                # 清空对话内容并恢复预设人设
                session['msg'] = [
                    {"role": "system", "content": config_data['chatgpt']['preset0']}
                ]
                session['character'] = 0
                return '人格已重置 当前人格：' + str(character_description[0])
            else:
                # 清空对话内容并恢复预设人设
                session['msg'] = [
                    {"role": "system", "content": config_data['chatgpt']['preset'+str(safe_preset)]}
                ]
                session['character'] = safe_preset
                return '人格已重置 当前人格：' + str(character_description[safe_preset])
        if '查询余额' == msg.strip():
            text = ""
            for i in range(len(config_data['openai']['api_key'])):
                text = text + "Key_" + str(i + 1) + " 余额: " + str(round(get_credit_summary_by_index(i), 2)) + "美元\n"
            return text
        if '指令说明' == msg.strip():
            return '指令如下(群内需@机器人或开头加上该人格的名字[仅预设])：\n1.[重置会话] 请发送 重置会话\n2.[切换人格] 请发送 "切换人格 人格预设"(发送"人格列表"可以查看所有人格预设)\n3.[自定义人格] 请发送 "自定义人格 <该人格的描述>"\n4.[人格列表] 请发送 人格列表\n5.[重置人格] 请发送 重置人格\n6.[忘记上一条对话]请发送 忘记上一条对话\n7.[当前人格] 请发送 当前人格\n8.[指令说明] 请发送 ' \
                   '指令说明\n9.[查看群聊对话模式] 请发送 查看群聊对话模式\n10.[添加权限] 请管理员发送 "添加权限 QQ号"\n10.[切换安全模式] 请管理员发送 切换安全模式\n[语音开启][语音关闭]\n注意：\n重置会话不会清空人格,重置人格会重置会话!\n设置人格后人格将一直存在，除非重置人格或重启逻辑端!'
        if msg.strip().startswith('/img'):
            msg = str(msg).replace('/img', '')
            print('开始直接生成图像')
            pic_path = get_openai_image(msg)
            return "![](" + pic_path + ")"
        if msg.strip().startswith('切换人格'):
            Characterlistener()
            uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
            if ((str(uid) in (advanced_users or moderator_qq)) or (safe_mode == False)):  # 若用户在advanced_users组中或安全模式关
                ques = msg.strip().replace('切换人格', '')     # 将msg（用户输入）中的"切换人格"删除
                ques = ques.strip()       # 将msg中的空白删除
                ques = ques.lower()     # 将msg中的字母全部转换为小写以供识别
                matched = False
                for i in range(0, len(character_description)-1):
                    if ques == character_description[i].lower():
                        session['msg'] = [
                            {"role": "system", "content": config_data['chatgpt']['preset'+str(i)]}
                        ]
                        session['character'] = i
                        matched = True
                        return '人格切换成功 当前人格：' + str(character_description[i])
                    elif ques == "": # 当输入空消息时
                        session['msg'] = [
                            {"role": "system", "content": config_data['chatgpt']['preset0']}# 切换至默认人格
                        ]
                        session['character'] = 0
                        matched = True
                        return '人格切换成功 当前人格：' + str(character_description[0])
                        break
                # 当用户输入与上述任何一种情况不匹配时
                if matched == False:
                    session['msg'] = [
                        {"role": "system", "content": ques}
                    ]                                                                       # 直接将输入自定义人设写入session
                    session['character'] = -1
                    return '人格切换成功 当前人格：自定义'
            else:
                return "错误：没有足够权限来执行此操作."
        if '当前人格' == msg.strip():
            desc = character_description[session['character']]
            return '当前人格：' + str(desc)
        if '查看群聊对话模式' == msg.strip():
            if request.get_json().get('message_type') == 'private':  # 如果是私聊信息
                return '错误：此指令仅能在群聊内使用.'
            else:
                gid = request.get_json().get('group_id')  # 群号
                # 判断群号是否在general_enabled_group中
                if (str(gid) in general_enabled_group):
                    return '当前模式：群聊共享对话'
                else:
                    return '当前模式：个人独立对话'
        if '切换群聊对话模式' == msg.strip():
            if request.get_json().get('message_type') == 'private':  # 如果是私聊信息
                return '错误：此指令仅能在群聊内使用.'
            else:
                gid = request.get_json().get('group_id')  # 群号
                uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
                # 检测用户是否为moderator
                if (str(uid) in moderator_qq): # 若拥有权限
                    # 重置人格
                    session['msg'] = [
                        {"role": "system", "content": config_data['chatgpt']['preset']}
                    ]
                    session['character'] = 0
                    # 判断群号是否在general_enabled_group中
                    if (str(gid) not in general_enabled_group):
                        general_enabled_group.append(str(gid))
                        return '群聊对话模式切换成功，会话及人格已重置 \n当前模式：群聊共享对话'
                    else:
                        general_enabled_group.remove(str(gid))
                        return '群聊对话模式切换成功，会话及人格已重置 \n当前模式：个人独立对话'
                else:
                    return "错误：没有足够权限来执行此操作."
        if '人格列表' == msg.strip():
            Characterlistener()
            out = "当前可切换人格：\n"
            for i in range(0, len(character_description)-1):
                out = out + str(character_description[i]) + "\n"
                Characterlistener()
            out = out + "(PS:使用'切换人格 人格预设'即可完成切换)"
            return out
        if msg.strip().startswith('自定义人格'):
            uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
            if (str(uid) in (advanced_users or moderator_qq)) or (safe_mode == False):#若用户在advanced_users组中或安全模式关
                # 清空对话并设置人设
                session['msg'] = [
                    {"role": "system", "content": msg.strip().replace('自定义人格', '')}
                ]
                session['character'] = -1
                return '自定义人格设置成功\n（提示：下次切换或重置人格前都会保持此人设）'
            else:
                return "错误：没有足够权限来执行此操作."
        if msg.strip().startswith('添加权限'):
            uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
            ques = msg.strip().replace('添加权限', '') # 去除消息中的'添加权限'
            ques = ques.strip()  # 去除空格
            # 检测用户是否为moderator
            if (str(uid) in moderator_qq): # 若拥有权限
                if ques == '':  # 若未键入任何uid
                    return "错误：输入值不能为空白."
                elif ques in advanced_users:
                    return "错误：此用户已经在advanced_users组中."
                else:
                    try:
                        int(ques) # 检测键入值是否为数字
                    except ValueError: # 若不是
                        return "错误：输入值必须为QQ号"
                    adv.advanced_users.append(str(ques)) # 添加该值
                    with open("adv.py", "w",encoding='utf-8') as f: # 打开adv.py
                        f.write("advanced_users = " + str(adv.advanced_users)) # 写入新的列表
                    return "用户权限添加成功"
            else:
                return "错误：没有足够权限来执行此操作."
        if msg.strip().startswith('删除权限'):
            uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
            ques = msg.strip().replace('删除权限', '') # 去除消息中的'删除权限'
            ques = ques.strip()  # 去除空格
            # 检测用户是否为moderator
            if (str(uid) in moderator_qq): # 若拥有权限
                if ques == '':
                    return "错误：输入值不能为空白."
                elif ques not in advanced_users:
                    return "错误：此用户不在advanced_users组中."
                else:
                    if ques in moderator_qq:
                        return "错误：无权移除该用户的权限组."
                    else:
                        try:
                            int(ques) # 检测键入值是否为数字
                        except ValueError: # 若不是
                            return "错误：输入值必须为QQ号"
                        adv.advanced_users.remove(str(ques)) # 去除该值
                        with open("adv.py", "w", encoding='utf-8') as f:  # 打开adv.py
                            f.write("advanced_users = " + str(adv.advanced_users)) # 写入新的列表
                        return "用户权限删除成功"
            else:
                return "错误：没有足够权限来执行此操作."
        if '切换安全模式' == msg.strip():
            uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
            # 检测用户是否为moderator
            if (str(uid) in moderator_qq): # 若拥有权限
                if safe_mode == False:
                    safe_mode = True
                    return '已开启人格切换限制（全局生效）'
                else:
                    safe_mode = False
                    return '已关闭人格限制（全局生效）'
            else:
                return "错误：没有足够权限来执行此操作."
        # 设置本次对话内容
        session['msg'].append({"role": "user", "content": msg})
        # 设置时间
        session['msg'][1] = {"role": "system", "content": "current time is:" + get_bj_time()}
        # 检查是否超过tokens限制
        while num_tokens_from_messages(session['msg']) > config_data['chatgpt']['max_tokens']:
            # 当超过记忆保存最大量时，清理一条
            del session['msg'][2:3]
        # 与ChatGPT交互获得对话内容
        message = chat_with_gpt(session['msg'])
        # 记录上下文
        session['msg'].append({"role": "assistant", "content": message})
        print("会话ID: " + str(sessionid))
        print("ChatGPT返回内容: ")
        print(message)
        return message
    except Exception as error:
        traceback.print_exc()
        return str('异常: ' + str(error))


# 获取北京时间
def get_bj_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)
    fmt = '%Y-%m-%d %H:%M:%S'
    now_fmt = beijing_now.strftime(fmt)
    return now_fmt


# 获取对话session
def get_chat_session(sessionid):
    if sessionid not in sessions:
        config = deepcopy(session_config)
        config['id'] = sessionid
        config['msg'].append({"role": "system", "content": "current time is:" + get_bj_time()})
        sessions[sessionid] = config
    return sessions[sessionid]


def chat_with_gpt(messages):
    global current_key_index
    max_length = len(config_data['openai']['api_key']) - 1
    try:
        if not config_data['openai']['api_key']:
            return "请设置Api Key"
        else:
            if current_key_index > max_length:
                current_key_index = 0
                return "全部Key均已达到速率限制,请等待一分钟后再尝试"
            openai.api_key = config_data['openai']['api_key'][current_key_index]

        resp = openai.ChatCompletion.create(
            model=config_data['chatgpt']['model'],
            messages=messages
        )
        resp = resp['choices'][0]['message']['content']
    except openai.OpenAIError as e:
        if str(e).__contains__("Rate limit reached for default-gpt-3.5-turbo") and current_key_index <= max_length:
            # 切换key
            current_key_index = current_key_index + 1
            print("速率限制，尝试切换key")
            return chat_with_gpt(messages)
        elif str(e).__contains__("Your access was terminated due to violation of our policies") and current_key_index <= max_length:
            print("请及时确认该Key: " + str(openai.api_key) + " 是否正常，若异常，请移除")
            if current_key_index + 1 > max_length:
                return str(e)
            else:
                print("访问被阻止，尝试切换Key")
                # 切换key
                current_key_index = current_key_index + 1
                return chat_with_gpt(messages)
        else:
            print('openai 接口报错: ' + str(e))
            resp = str(e)
    if str(resp).__contains__("HTTP code 504 from API"):
        resp = "(っ´ωc)　呜哇哇，Close AI 一点都不理我，我不知道说什么了啦 ｡ﾟ(ﾟ´ωﾟ)ﾟ｡ "
    return resp


# 生成图片
def genImg(message):
    img = text_to_image(message)
    filename = str(uuid.uuid1()) + ".png"
    filepath = config_data['qq_bot']['image_path'] + str(os.path.sep) + filename
    img.save(filepath)
    print("图片生成完毕: " + filepath)
    return filename


# 发送私聊消息方法 uid为qq号，message为消息内容
def send_private_message(uid, message, send_voice):
    try:
        if send_voice:  # 如果开启了语音发送
            voice_path = asyncio.run(
                gen_speech(message, config_data['qq_bot']['voice'], config_data['qq_bot']['voice_path']))
            message = "[CQ:record,file=file://" + voice_path + "]"
        if len(message) >= config_data['qq_bot']['max_length'] and not send_voice:  # 如果消息长度超过限制，转成图片发送
            pic_path = genImg(message)
            message = "[CQ:image,file=" + pic_path + "]"
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            print("私聊消息发送成功")
        else:
            print(res)
            print("私聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        print("私聊消息发送失败")
        print(error)


# 发送私聊消息方法 uid为qq号，pic_path为图片地址
def send_private_message_image(uid, pic_path, msg):
    try:
        message = "[CQ:image,file=" + pic_path + "]"
        if msg != "":
            message = msg + '\n' + message
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            print("私聊消息发送成功")
        else:
            print(res)
            print("私聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        print("私聊消息发送失败")
        print(error)


# 发送群消息方法
def send_group_message(gid, message, uid, send_voice):
    try:
        if send_voice:  # 如果开启了语音发送
            voice_path = asyncio.run(
                gen_speech(message, config_data['qq_bot']['voice'], config_data['qq_bot']['voice_path']))
            message = "[CQ:record,file=file://" + voice_path + "]"
        if len(message) >= config_data['qq_bot']['max_length'] and not send_voice:  # 如果消息长度超过限制，转成图片发送
            pic_path = genImg(message)
            message = "[CQ:image,file=" + pic_path + "]"
        if not send_voice:
            message = str('[CQ:at,qq=%s]\n' % uid) + message  # @发言人
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            print("群消息发送成功")
        else:
            print("群消息发送失败，错误信息：" + str(res['wording']))
    except Exception as error:
        print("群消息发送失败")
        print(error)


# 发送群消息图片方法
def send_group_message_image(gid, pic_path, uid, msg):
    try:
        message = "[CQ:image,file=" + pic_path + "]"
        if msg != "":
            message = msg + '\n' + message
        message = str('[CQ:at,qq=%s]\n' % uid) + message  # @发言人
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            print("群消息发送成功")
        else:
            print("群消息发送失败，错误信息：" + str(res['wording']))
    except Exception as error:
        print("群消息发送失败")
        print(error)


# 处理好友请求
def set_friend_add_request(flag, approve):
    try:
        requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/set_friend_add_request",
                      params={'flag': flag, 'approve': approve})
        print("处理好友申请成功")
    except:
        print("处理好友申请失败")


# 处理邀请加群请求
def set_group_invite_request(flag, approve):
    try:
        requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/set_group_add_request",
                      params={'flag': flag, 'sub_type': 'invite', 'approve': approve})
        print("处理群申请成功")
    except:
        print("处理群申请失败")


# openai生成图片
def get_openai_image(des):
    openai.api_key = config_data['openai']['api_key'][current_key_index]
    response = openai.Image.create(
        prompt=des,
        n=1,
        size=config_data['openai']['img_size']
    )
    image_url = response['data'][0]['url']
    print('图像已生成')
    print(image_url)
    return image_url


# 查询账户余额
def get_credit_summary():
    url = "https://chat-gpt.aurorax.cloud/dashboard/billing/credit_grants"
    res = requests.get(url, headers={
        "Authorization": f"Bearer " + config_data['openai']['api_key'][current_key_index]
    }, timeout=60).json()
    return res


# 查询账户余额
def get_credit_summary_by_index(index):
    url = "https://chat-gpt.aurorax.cloud/dashboard/billing/credit_grants"
    res = requests.get(url, headers={
        "Authorization": f"Bearer " + config_data['openai']['api_key'][index]
    }, timeout=60).json()
    return res['total_available']


# 计算消息使用的tokens数量
def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # 如果name字段存在，role字段会被忽略
                    num_tokens += -1  # role字段是必填项，并且占用1token
        num_tokens += 2
        return num_tokens
    else:
        raise NotImplementedError(f"""当前模型不支持tokens计算: {model}.""")


if __name__ == '__main__':
    server.run(port=5555, host='0.0.0.0', use_reloader=False)
