import requests
import json
import time
import global_var

def get_latest_post(mid):
    '''
    '''
    url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid=24004198&type=268435455"
    r = requests.get(url=url, headers=global_var.headers)
    content = json.loads(r.text)
    latest_mid = content["data"]["cards"][0]["desc"]['uid']
    if latest_mid == mid :
        print("\n\n！！！是喵！！！！\n\n")
        return 1
    else: 
        print("=============")
        return 0
    

v = 0
while v == 0:
    v = get_latest_post(3267519)
    time.sleep(10)