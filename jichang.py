#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://github.com/yunzimo/KDCheckin/tree/2.11.3/jichang.py

"""
File: jichang.py
Author: yunzimo
Date: 2023/04/07
cron: 10 8,10 * * *
new Env('机场签到');
Description: 需要在环境变量中添加JC_COOKIE,主要CK参数有uid、email、key、expire_in
"""


import json
import requests
import re
import time
import os,sys

from notify import *

content = ''

def get_cookies():
    CookieJCs = []
    if os.environ.get("JC_COOKIE"):
        print("已获取并使用Env环境 Cookie")
        if '&' in os.environ["JC_COOKIE"]:
            CookieJCs = os.environ["JC_COOKIE"].split('&')
        elif '\n' in os.environ["JC_COOKIE"]:
            CookieJCs = os.environ["JC_COOKIE"].split('\n')
        else:
            CookieJCs = [os.environ["JC_COOKIE"]]
    else:
        print("未获取到正确✅格式的机场账号Cookie")
        return

    print(f"====================共{len(CookieJCs)}个机场账号Cookie=========\n")
    print(f"==================脚本执行- 北京时间(UTC+8)：{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}=====================\n")
    return CookieJCs
if __name__ == '__main__':
    try:
        cks = get_cookies()
        if not cks:
            sys.exit()
    except:
        print("未获取到有效COOKIE,退出程序！")
        sys.exit()
    for cookie in cks[:]:
        print('cookie:'+cookie+'\n')
        try:
            header = {
            'cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 '
                            'Safari/537.36 '
            }
            response = requests.post("https://www.cutecloud.net/user/checkin", headers=header)
            print(response.status_code)
            if response.status_code != 200:
                print('机场签到失败，可能是cookie失效了')
                send('机场签到','机场签到失败，可能是cookie失效了')
            else:
                print(response.text)
                result = json.loads(response.text)
                if result['ret']==1:
                    print('result中trafficInfo的类型'+type(result['trafficInfo']))
                    trafficInfo = json.loads(str(result['trafficInfo']))
                    content = content + result['msg'] + '\n' +'今日使用：'+ trafficInfo['todayUsedTraffic']+'\n'+'总共使用：'+trafficInfo['lastUsedTraffic']+'\n'+'流量剩余：'+trafficInfo['unUsedTraffic']+'\n'
                    send('机场签到','签到成功' + content)            
                else:
                    content = content + result['msg']
                    print(content)
                    send('机场签到',content)
        except Exception:
            print('机场签到失败\n')
            traceback.print_exc()
            send('机场签到','机场签到失败'+traceback.format_exc())