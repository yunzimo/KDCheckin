# -*- coding: utf-8 -*-
"""
cron: 55 7 * * *
new Env('{签到的标题}');
"""

import requests, time, re, json, sys, traceback
from io import StringIO
from KDconfig import getYmlConfig
from KDsrc.sendNotify import *

class Cloud:
    def __init__(self, cookie):
        self.sio = StringIO()
        self.Cookies = cookie
        self.cookie = ''

    def SignIn(self):
        print("【{签到的标题} 日志】")
        self.sio.write("【{签到的标题}】\n")
        for cookie in self.Cookies:
            cookie = cookie.get("user")
            print(f"{cookie.get('name')} 开始签到...")
            self.sio.write(f"{cookie.get('name')}: ")
            self.cookie = cookie.get('cookie')
            try:
                self.Sign_in()
            except:
                print(f"{cookie.get('name')}: 异常 {traceback.format_exc()}")
                if '签到存在异常, 请自行查看签到日志' not in self.sio.getvalue():
                    self.sio.write('签到存在异常, 请自行查看签到日志\n')
        return self.sio

if __name__ == '__main__':
    config = getYmlConfig('Cookie.yml')
    Cookies = config.get('Cloud')
    if Cookies != None:
        if Cookies.get('cookies') != None:
            cloud = Cloud(Cookies['cookies'])
            sio = cloud.SignIn()
            print(f'\n{sio.getvalue()}')
            if Cookies.get('send') != None and Cookies['send'] == 1:
                send('{签到的标题}', sio.getvalue())
            else:
                print('推送失败: 关闭了推送 or send配置问题')
        else:
            print('配置文件 {签到的标题} 没有 "cookies"')
            sys.exit()
    else:
        print('配置文件没有 {签到的标题}')