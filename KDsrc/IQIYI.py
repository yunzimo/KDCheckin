# -*- coding: utf-8 -*-
"""
cron: 55 7 * * *
new Env('爱奇艺');
"""

import requests, time, re, json, sys, traceback
from io import StringIO
from KDconfig import getYmlConfig
from KDsrc.sendNotify import *
from urllib.parse import unquote

class IQIYI:
    def __init__(self, cookie):
        self.sio = StringIO()
        self.Cookies = cookie
        self.cookie = ''

    def parse_cookie(self, cookie):
        p00001 = re.findall(r"P00001=(.*?);", cookie)[0]
        p00002 = re.findall(r"P00002=(.*?);", cookie)[0] if re.findall(r"P00002=(.*?);", cookie) else ""
        p00003 = re.findall(r"P00003=(.*?);", cookie)[0]
        return p00001, p00002, p00003

    def user_information(self, p00001):
        """
        用户信息查询
        """
        url = "http://serv.vip.iqiyi.com/vipgrowth/query.action"
        params = {"P00001": p00001}
        res = requests.get(url=url, params=params).json()
        if res["code"] == "A00000":
            try:
                res_data = res.get("data", {})
                level = res_data.get("level", 0)  # VIP 等级
                growthvalue = res_data.get("growthvalue", 0)  # 当前 VIP 成长值
                distance = res_data.get("distance", 0)  # 升级需要成长值
                deadline = res_data.get("deadline", "非 VIP 用户")  # VIP 到期时间
                today_growth_value = res_data.get("todayGrowthValue", 0)  # 今日成长值
                msg = [
                    {"name": "VIP 等级", "value": level},
                    {"name": "当前成长值", "value": growthvalue},
                    {"name": "升级需成长值", "value": distance},
                    {"name": "今日成长值", "value": today_growth_value},
                    {"name": "VIP 到期时间", "value": deadline},
                ]
            except Exception as e:
                msg = [
                    {"name": "用户信息", "value": str(e)},
                ]
                print(msg)
        else:
            msg = [
                {"name": "用户信息", "value": res.get("msg")},
            ]
        return msg

    def sign(self, p00001):
        """
        VIP 签到
        """
        url = "https://tc.vip.iqiyi.com/taskCenter/task/queryUserTask"
        params = {"P00001": p00001, "autoSign": "yes"}
        res = requests.get(url=url, params=params).json()
        if res["code"] == "A00000":
            try:
                growth = res["data"]["signInfo"]["data"]["rewardMap"]["growth"]
                cumulate_sign_days_sum = res["data"]["signInfo"]["data"]["cumulateSignDaysSum"]
                msg = [
                    {"name": "签到奖励", "value": f"{growth}成长值"},
                    {"name": "当月签到", "value": f"{cumulate_sign_days_sum}天"},
                ]
            except Exception as e:
                print(e)
                msg = [{"name": "签到奖励", "value": res["data"]["signInfo"].get("msg")}]
        else:
            msg = [{"name": "签到奖励", "value": res.get("msg")}]
        return msg

    def query_user_task(self, p00001):
        """
        获取 VIP 日常任务 和 taskCode(任务状态)
        """
        url = "https://tc.vip.iqiyi.com/taskCenter/task/queryUserTask"
        params = {"P00001": p00001}
        task_list = []
        res = requests.get(url=url, params=params).json()
        if res["code"] == "A00000":
            for item in res["data"]["tasks"]["daily"]:
                task_list.append(
                    {
                        "name": item["name"],
                        "taskCode": item["taskCode"],
                        "status": item["status"],
                        "taskReward": item["taskReward"]["task_reward_growth"],
                    }
                )
        return task_list

    def join_task(self, p00001, task_list):
        """
        遍历完成任务
        """
        url = "https://tc.vip.iqiyi.com/taskCenter/task/joinTask"
        params = {"P00001": p00001, "taskCode": "", "platform": "bb136ff4276771f3", "lang": "zh_CN"}
        for item in task_list:
            if item["status"] == 2:
                params["taskCode"] = item["taskCode"]
                requests.get(url=url, params=params)

    def get_task_rewards(self, p00001, task_list):
        """
        获取任务奖励
        :return: 返回信息
        """
        url = "https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards"
        params = {"P00001": p00001, "taskCode": "", "platform": "bb136ff4276771f3", "lang": "zh_CN"}
        growth_task = 0
        for item in task_list:
            if item["status"] == 0:
                params["taskCode"] = item.get("taskCode")
                requests.get(url=url, params=params)
            elif item["status"] == 4:
                requests.get(url="https://tc.vip.iqiyi.com/taskCenter/task/notify", params=params)
                params["taskCode"] = item.get("taskCode")
                requests.get(url=url, params=params)
            elif item["status"] == 1:
                growth_task += item["taskReward"]
        msg = {"name": "任务奖励", "value": f"+{growth_task}成长值"}
        return msg

    def draw(self, draw_type, p00001, p00003):
        """
        查询抽奖次数(必),抽奖
        :param draw_type: 类型。0 查询次数；1 抽奖
        :param p00001: 关键参数
        :param p00003: 关键参数
        :return: {status, msg, chance}
        """
        url = "https://iface2.iqiyi.com/aggregate/3.0/lottery_activity"
        params = {
            "lottery_chance": 1,
            "app_k": "b398b8ccbaeacca840073a7ee9b7e7e6",
            "app_v": "11.6.5",
            "platform_id": 10,
            "dev_os": "8.0.0",
            "dev_ua": "FRD-AL10",
            "net_sts": 1,
            "qyid": "2655b332a116d2247fac3dd66a5285011102",
            "psp_uid": p00003,
            "psp_cki": p00001,
            "psp_status": 3,
            "secure_v": 1,
            "secure_p": "GPhone",
            "req_sn": round(time.time() * 1000),
        }
        if draw_type == 1:
            del params["lottery_chance"]
        res = requests.get(url=url, params=params).json()
        if not res.get("code"):
            chance = int(res.get("daysurpluschance"))
            msg = res.get("awardName")
            return {"status": True, "msg": msg, "chance": chance}
        else:
            try:
                msg = res.get("kv", {}).get("msg")
            except Exception as e:
                print(e)
                msg = res["errorReason"]
        return {"status": False, "msg": msg, "chance": 0}

    def Sign_in(self):
        p00001, p00002, p00003 = self.parse_cookie(self.cookie)
        sign_msg = self.sign(p00001=p00001)
        chance = self.draw(0, p00001=p00001, p00003=p00003)["chance"]
        if chance:
            draw_msg = ""
            for i in range(chance):
                ret = self.draw(1, p00001=p00001, p00003=p00003)
                draw_msg += ret["msg"] + ";" if ret["status"] else ""
        else:
            draw_msg = "抽奖机会不足"
        task_msg = ""
        for one in range(6):
            task_list = self.query_user_task(p00001=p00001)
            self.join_task(p00001=p00001, task_list=task_list)
            time.sleep(10)
            task_msg = self.get_task_rewards(p00001=p00001, task_list=task_list)
        try:
            user_info = json.loads(unquote(p00002, encoding="utf-8"))
            user_name = user_info.get("user_name")
            user_name = user_name.replace(user_name[3:7], "****")
            nickname = user_info.get("nickname")
        except Exception as e:
            print(f"获取用户信息失败，错误信息: {e}")
            nickname = "未获取到，请检查 Cookie 中 P00002 字段"
            user_name = "未获取到，请检查 Cookie 中 P00002 字段"
        user_msg = self.user_information(p00001=p00001)

        msg = (
            [
                {"name": "用户账号", "value": user_name},
                {"name": "用户昵称", "value": nickname},
            ]
            + user_msg
            + sign_msg
            + [
                task_msg,
                {"name": "抽奖奖励", "value": draw_msg},
            ]
        )
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        self.sio.write(msg+'\n')
        print(msg+'\n')

    def SignIn(self):
        print("【爱奇艺 日志】")
        self.sio.write("【爱奇艺】\n")
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
    Cookies = config.get('IQIYI')
    if Cookies != None:
        if Cookies.get('cookies') != None:
            iqiyi = IQIYI(Cookies['cookies'])
            sio = iqiyi.SignIn()
            print(f'\n{sio.getvalue()}')
            if Cookies.get('send') != None and Cookies['send'] == 1:
                send('爱奇艺', sio.getvalue())
            else:
                print('推送失败: 关闭了推送 or send配置问题')
        else:
            print('配置文件 爱奇艺 没有 "cookies"')
            sys.exit()
    else:
        print('配置文件没有 爱奇艺')