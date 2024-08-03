# -*- coding: utf-8 -*-
from qg_botsdk import BOT, Model
from openai import OpenAI
import os
import json
from datetime import datetime
import re


bot = BOT(bot_id="102070552", bot_token="qHAvc3v8Me2XvIdspk4MgWPcEcAsN2A3", is_private=True , is_sandbox=False)
with open('wash.txt', 'r',encoding='utf-8') as file:
    wash=file.read()
with open('check.txt', 'r',encoding='utf-8') as file:
    check=file.read()

def deepseek(msg,prompt):
    client = OpenAI(api_key="sk-5939c8ddb4ce4902a97b13e87ad02779", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role":"system",
                "content": prompt
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
    #bot.logger.info(f'response={response}')
    bot.logger.info(f'prompt_cache_hit_tokens={response.usage.prompt_cache_hit_tokens}')
    bot.logger.info(f'prompt_cache_miss_tokens={response.usage.prompt_cache_miss_tokens}')
    return response.choices[0].message.content
    
    
def translate(meseage):
    msg=json.loads(meseage)
    #bot.logger.info(msg)
    if msg['委托表'] != '通过':
        return msg['委托表']
    reply = ''
    for value in msg.values():
        #bot.logger.info(f'Value: {value}')
        if value!='通过':
            reply += f'{value}\n'
    return reply

def is_at(user):
    bot_id = bot.api.get_bot_info().data.id
    return any(item.id == bot_id for item in user) 

def getId(guild_id,name):
    lst=bot.api.get_guild_roles(guild_id)
    #bot.logger.info(lst)
    for sf in lst.data.roles:
        if sf.name in name:
            return sf.id

def query(msg):
    time1=datetime.now()
    if '深渊使用率' in msg or '角色持有' in msg:
        return '玩原神玩的'
    #bot.logger.info('###msg\n'+msg+'\n###msg\n')
    reply1=deepseek(msg,wash)
    #bot.logger.info('###reply1\n'+reply1+'\n###reply1\n')
    reply2=deepseek(reply1,check)
    #bot.logger.info('###reply2\n'+reply2+'\n###reply2\n')
    reply=translate(reply2)
    time2=datetime.now()
    bot.logger.info('AI共花费了：')
    bot.logger.info(time2 - time1)
    return reply


@bot.bind_msg()
def deliver(data: Model.MESSAGE):

    time1=datetime.now()
    channelName=bot.api.get_guild_info(data.guild_id).data.name
    if (channelName=='幽灵的频道'):
        return
    formal_id=getId(data.guild_id,['正式成员'])
    #bot.logger.info(data.author.username+":"+data.treated_msg)
    #bot.logger.info(data)    
    #bot.logger.info('频道名：'+channelName)
    #bot.logger.info(data.content)
    #bot.logger.info(data.treated_msg)bot.logger.info
    #bot.logger.info('@小灵bot' in data.treated_msg)
    reply=''
    cleaned_msg = re.sub(r'<@!\d+>', '', data.content)
    #bot.logger.info(len(cleaned_msg))
    #bot.logger.info('过' in cleaned_msg)
    #bot.logger.info(cleaned_msg)

    success='你通过了考核，可以去互助区发帖找人互助了。发完帖后不要等别人找你，主动找别人互助效率更高\n'
    if (len(cleaned_msg)<5 and '过' in cleaned_msg):
        #bot.logger.info('已经检测到 过 指令')
        lst = bot.api.get_guild_roles(data.guild_id)
        adminIds = [sf.id for sf in lst.data.roles if '管理' in sf.name]
        authorIds = data.member.roles
        #bot.logger.info(f'adminIds:{adminIds}')
        #bot.logger.info(f'authorIds:{authorIds}')
        if (set(adminIds) & set(authorIds)):
            #bot.logger.info('指令 发起人为管理员')
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
        bot.logger.info('机器人准备回复了')
        data.reply('机器人正在审核')
        reply=query(data.treated_msg)
        head='<@'+data.author.id+'>'+'\n'
        if reply=='':
            bot.logger.info(data.author.username+' 成功通过考核')
            bot.api.create_role_member(user_id=data.author.id,guild_id=data.guild_id,role_id=formal_id)
            reply+=success
        data.reply(head+reply,message_reference_id=data.id) 
    time2=datetime.now()   
    bot.logger.info('回复消息共花费了：')
    bot.logger.info(time2 - time1)
@bot.bind_forum()
def forum_function(data: Model.FORUMS_EVENT):
    if data.t != 'FORUM_THREAD_CREATE':
        return
    formal_id=getId(data.guild_id,['正式成员'])
    #bot.logger.info(data)
    #bot.logger.info(data.thread_info)
    user=bot.api.get_member_info(data.guild_id,data.author_id)
    roles=user.data.roles
    if formal_id in roles:
        return
    bot.logger.info('非正式成员'+user.data.user.username+'发帖')
    bot.api.delete_thread(data.channel_id,data.thread_info.thread_id)
    bot.logger.info('已清除非法帖子')
    direct_id=bot.api.create_dm_guild(data.author_id,data.guild_id).data.guild_id
    #bot.logger.info(direct_id)
    content='由于很多人的举报信息收集表填写不完整，导致互助效率极度低下，故本频道需要通过考核后才能发帖。请先看公告，再去考核区参与考核。'
    bot.api.send_dm(guild_id=direct_id,content=content,message_id=data.thread_info.thread_id)
    bot.logger.info('已提醒成员先去考核区考核')

if __name__ == "__main__":
    bot.start()


