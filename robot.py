# -*- coding: utf-8 -*-
from qg_botsdk import BOT, Model
from openai import OpenAI
import os
import json

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
    return response.choices[0].message.content
    
    
def translate(meseage):
    msg=json.loads(meseage)
    #print(msg)
    if msg['委托表'] != '通过':
        return msg['委托表']
    reply = ''
    for value in msg.values():
        print(f'Value: {value}')
        if value!='通过':
            reply += f'{value}\n'
    return reply

def is_at(users):
    x=bot.api.get_bot_info().data.id
    for i in users:
        if (x==i.id):
            return True
    return False     
def setFormal(data):
    lst=bot.api.get_guild_roles(data.guild_id)
    #print(lst)
    id=0
    for sf in lst.data.roles:
        if sf.name=='正式成员':
            id=sf.id
            break
    bot.api.create_role_member(user_id=data.author.id,guild_id=data.guild_id,role_id=id)
def query(msg):
    if '深渊使用率' in msg or '角色持有' in msg:
        return '玩原神玩的'
    print('###msg\n'+msg+'\n###msg\n')
    reply1=deepseek(msg,'wash.txt')
    print('###reply1\n'+reply1+'\n###reply1\n')
    reply2=deepseek(reply1,'check.txt')
    print('###reply2\n'+reply2+'\n###reply2\n')
    reply=translate(reply2)
    return reply

@bot.bind_msg()
def deliver(data: Model.MESSAGE):
    #print(data.author.username+":"+data.treated_msg)
    #print(data)
    if ('mentions' not in data.__dict__):
        return
    if is_at(data.mentions):
        reply=query(data.treated_msg)
        head='<@'+data.author.id+'>'+'\n'
        if reply=='':
            print('  '+data.author.username+'成功通过考核')
            setFormal(data)
            reply+='你通过了考核，可以去互助区发帖找人互助了。发完帖后不要等别人找你，主动找别人互助效率更高\n'
        data.reply(head+reply,message_reference_id=data.id) 

if __name__ == "__main__":
    bot.start()


