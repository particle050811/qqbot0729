# -*- coding: utf-8 -*-
from qg_botsdk import BOT, Model
from openai import OpenAI
import os
import json
from datetime import datetime
import re
bot = BOT(bot_id="102070552", bot_token="qHAvc3v8Me2XvIdspk4MgWPcEcAsN2A3", is_private=True , is_sandbox=False)


def deepseek(msg,filename='check.txt'):
    client = OpenAI(api_key="sk-5939c8ddb4ce4902a97b13e87ad02779", base_url="https://api.deepseek.com")
    #print('filename='+filename)
    with open(filename, 'r',encoding='utf-8') as file:
        system_prompt=file.read()
    #print("system_prompt:"+system_prompt)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role":"system",
                "content": system_prompt
            }, 
            {
                "role": "user", 
                "content": msg
            }
            
        ],
        response_format={
            'type': 'json_object'
        }
    )
    #print(f'response={response}')
    print(f'prompt_cache_hit_tokens={response.usage.prompt_cache_hit_tokens}')
    print(f'prompt_cache_miss_tokens={response.usage.prompt_cache_miss_tokens}')
    return response.choices[0].message.content
    
    
def translate(meseage):
    msg=json.loads(meseage)
    #print(msg)
    if msg['委托表'] != '通过':
        return msg['委托表']
    reply = ''
    for value in msg.values():
        #print(f'Value: {value}')
        if value!='通过':
            reply += f'{value}\n'
    return reply

def is_at(user):
    bot_id = bot.api.get_bot_info().data.id
    return any(item.id == bot_id for item in user) 

def getId(guild_id,name):
    lst=bot.api.get_guild_roles(guild_id)
    #print(lst)
    for sf in lst.data.roles:
        if sf.name in name:
            return sf.id

def query(msg):
    time1=datetime.now()
    if '深渊使用率' in msg or '角色持有' in msg:
        return '玩原神玩的'
    #print('###msg\n'+msg+'\n###msg\n')
    reply1=deepseek(msg,'wash.txt')
    #print('###reply1\n'+reply1+'\n###reply1\n')
    reply2=deepseek(reply1,'check.txt')
    #print('###reply2\n'+reply2+'\n###reply2\n')
    reply=translate(reply2)
    time2=datetime.now()
    print('AI共花费了：',end='')
    print(time2 - time1)
    return reply

@bot.bind_msg()
def deliver(data: Model.MESSAGE):

    time1=datetime.now()
    channelName=bot.api.get_guild_info(data.guild_id).data.name
    if (channelName=='幽灵的频道'):
        return
    formal_id=getId(data.guild_id,['正式成员'])
    #print(data.author.username+":"+data.treated_msg)
    #print(data)    
    #print('频道名：'+channelName)
    #print(data.content)
    #print(data.treated_msg)
    #print('@小灵bot' in data.treated_msg)
    reply=''
    cleaned_msg = re.sub(r'<@!\d+>', '', data.content)
    #print(len(cleaned_msg))
    #print('过' in cleaned_msg)
    #print(cleaned_msg)
    success='你通过了考核，可以去互助区发帖找人互助了。发完帖后不要等别人找你，主动找别人互助效率更高\n'
    if (len(cleaned_msg)<5 and '过' in cleaned_msg):
        #print('已经检测到 过 指令')
        lst = bot.api.get_guild_roles(data.guild_id)
        adminIds = [sf.id for sf in lst.data.roles if '管理' in sf.name]
        authorIds = data.member.roles
        #print(f'adminIds:{adminIds}')
        #print(f'authorIds:{authorIds}')
        if (set(adminIds) & set(authorIds)):
            #print('指令 发起人为管理员')
            if ('mentions' not in data.__dict__):
                data.reply('你没有指定任何人设置为正式成员',message_reference_id=data.id)
                return
            for member in data.mentions:
                bot.api.create_role_member(user_id=member.id,guild_id=data.guild_id,role_id=formal_id)
                reply+='<@'+member.id+'>'
            data.reply('已将'+reply+'设置为正式成员'+'\n'+success,message_reference_id=data.id)
        else:
            data.reply('你不是管理员，没有使用该指令的权限。',message_reference_id=data.id)
        return    

    
    if ('mentions' in data.__dict__ and is_at(data.mentions)) or '@小灵bot' in data.treated_msg:
        print('机器人准备回复了')
        reply=query(data.treated_msg)
        head='<@'+data.author.id+'>'+'\n'
        if reply=='':
            print('  '+data.author.username+'成功通过考核')
            bot.api.create_role_member(user_id=data.author.id,guild_id=data.guild_id,role_id=formal_id)
            reply+=success
        data.reply(head+reply,message_reference_id=data.id) 
    time2=datetime.now()   
    print('回复消息共花费了：',end='')
    print(time2 - time1)

if __name__ == "__main__":
    bot.start()


