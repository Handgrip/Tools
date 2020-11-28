#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import base64
import os
import json
import re
import platform
import time
HOST = "10.255.255.13"
INIT = f"http://{HOST}/index.php/index/init"
LOGOUT = f"http://{HOST}/index.php/index/logout"
LOGIN = f"http://{HOST}/index.php/index/login"

HEADERS = {
    "user-agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "accept": r"application/json, text/javascript, */*; q=0.01",
    "Connection": r"close"
}
TIMEOUT = 2
USERS = [
    ("电信", "18011111111", "111111"),
    ("移动", "18011111111", "111111"),
    ("联通", "18011111111", "111111")
]
ALTDOMAIN = {
    "电信": "ChinaNet",
    "移动": "CMCC",
    "联通": "Unicom"
}


def PrintStatus():
    ret = requests.get(url=INIT, headers=HEADERS, timeout=TIMEOUT).json()
    if ret["status"] == 1:
        seconds = ret["logout_timer"]
        if seconds >= 0:
            ret["logout_timer"] = "%02d:%02d:%02d" % (
                seconds//3600, seconds % 3600//60, seconds % 60)
    for key, val in ret.items():
        print(f"{key}: {val}")
    print("")
    if ret["status"] == 1:
        try:
            PrintIpInfo()
        except:
            print("获取公网 ip 出错")


def PrintIpInfo():
    ret = requests.get(url="https://202020.ip138.com",
                       headers=HEADERS, timeout=TIMEOUT)
    ipurl = re.search(
        r'href="(https://www\.ip138\.com/iplookup\.asp\?ip=[\d\.]*?&action=\d*)"', ret.content.decode("utf-8")).group(1)
    ret = requests.get(url=ipurl, headers=HEADERS, timeout=TIMEOUT)
    ipinfo = re.search(r'var ip_result = (.*?);',
                       ret.content.decode("gb2312")).group(1)
    print("公网 ip:", re.search(r'ip=([\d\.]*?)&', ipurl).group(1))
    print("ASN 归属地:", *json.loads(ipinfo)["ASN归属地"].split())
    print("")


def Logout():
    for key, val in requests.get(url=LOGOUT, headers=HEADERS, timeout=TIMEOUT).json().items():
        print(f"{key}: {val}")
    print("")


def Login(domain, username, password):
    password = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    domain = ALTDOMAIN[domain] if domain in ALTDOMAIN else None
    data = {
        "username": username,
        "password": password,
        "domain": domain
    }
    for key, val in requests.post(url=LOGIN, headers=HEADERS, timeout=TIMEOUT, data=data).json().items():
        print(f"{key}: {val}")
    print("")


def CleanScreen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def PrintMenu():
    for index, item in enumerate(USERS):
        print(f"{index+1}. {item[0]} {item[1]}")
    print("w. 注销")
    print("q. 退出")
    print("")


def Run():
    while True:
        CleanScreen()
        PrintStatus()
        PrintMenu()
        choice = input().split()[0]
        if choice == "q":
            print("Bye!")
            time.sleep(0.5)
            return
        elif choice == "w":
            Logout()
            time.sleep(1)
        elif choice == "r":
            pass
        elif choice.isdigit() and int(choice) <= len(USERS) and int(choice) >= 1:
            choice = int(choice) - 1
            Logout()
            time.sleep(1)
            Login(*USERS[choice])
            time.sleep(2)
        else:
            print("请输入正确的参数")
            time.sleep(1)


try:
    Run()
except requests.exceptions.ConnectionError as e:
    print("请检查网络")
    input("按任意键退出")
except KeyboardInterrupt:
    pass
except BaseException as e:
    print(repr(e))
    input("按任意键退出")
