"""AI utilities"""
from g4f.client import Client
import g4f
import json
import os
import time

print('AI client initialization')
temperature=os.getenv('AI_TEMPERATURE')
if not temperature:
    temperature = 1.18
client = Client()
print('AI client is ready')

with open('ai_system_message.txt') as file:
    system = file.readline()

def gpt(msgs):
    """Takes message history (list of strings) and returns ai response"""
    global client
    start_time = time.time()
    response = client.chat.completions.create(
        model="dolphin-3.0-24b",
        provider=g4f.Provider.Blackbox,
        temperature=temperature,
        web_search=False,
        messages=[
            {"role": "system",
             "content": system
            }
        ]+msgs
    )
    resp=response.choices[0].message.content.strip()
    msgs+=[{"role":"assistant","content":resp}]
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