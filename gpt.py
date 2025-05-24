"""AI utilities"""
from g4f.client import Client
import g4f
import json
import os
import time

print('AI client initialization')
temperature=os.getenv('AI_TEMPERATURE')
if not temperature:
    temperature = 0.5
client = Client()
print('AI client is ready')

with open('ai_system_message.txt', encoding='utf-8') as file:
    system = file.read()

def gpt(msg):
    """Takes message history (list of strings) and returns ai response"""
    global client
    start_time = time.time()
    response = client.chat.completions.create(
        model="deepseek-v3",
        provider=g4f.Provider.LambdaChat,
        temperature=temperature,
        web_search=False,
        messages=[
            {"role": "user",
             "content": system+'\n'+msg
            },
        ]
    )
    resp=response.choices[0].message.content.strip()
    # msgs+=[{"role":"assistant","content":resp}]
    return {"content":resp,"time_elapsed": time.time()-start_time}
    # try:
    #     return json.loads(resp[8:-4])
    # except Exception as e:
    #     print(e)
    #     try:
    #         return json.loads(resp)
    #     except Exception as e:
    #         print(resp)
    #         return {"role":"platform",'content':'Can not parse JSON response'}