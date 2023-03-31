import yaml, os, requests, json
import time, hmac, hashlib,  base64, urllib.parse

def getYmlConfig(yaml_file='Cookie.yml'):
    ql_file = '/ql/config/env.sh'
    cookie_file = '/ql/config/Cookie.yml'
    if os.path.exists(ql_file):
        if os.path.exists(cookie_file):
            file = open(cookie_file, 'r', encoding="utf-8")
        else:
            print('未找到Cookie的配置文件\n请执行下面的命令行\ncp /ql/repo/KD-happy_QingLongCheckin/Cookie.yml /ql/config/Cookie.yml')
            return {}
    else:
        if os.path.exists(yaml_file):
            file = open(yaml_file, 'r', encoding="utf-8")
        else:
            print('当前目录下没有配置文件Cookie.yml')
            return {}
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)

