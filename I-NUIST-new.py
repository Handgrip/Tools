#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import os
import json
import re
import platform
import time
HOST = "10.255.255.34"
LOGOUT = f"http://{HOST}/api/v1/logout"
LOGIN = f"http://{HOST}/api/v1/login"
IP = f"http://{HOST}/api/v1/ip"
os.environ['no_proxy'] = '*'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "application/json, text/plain, */*",
    # "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    # "Accept-Encoding": "gzip, deflate",
    # "Content-Type": "application/json;charset=utf-8",
    # "X-KL-Ajax-Request": "Ajax_Request",
    # "Origin": "http://10.255.255.34",
    "Connection": "Close",
    # "Referer": "http://10.255.255.34/authentication/login",
    # "Sec-Fetch-Dest": "empty",
    # "Sec-Fetch-Mode": "no-cors",
    # "Sec-Fetch-Site": "cross-site",
    # "Pragma": "no-cache",
    # "Cache-Control": "no-cache",
    # "TE": "trailers",
}
TIMEOUT = 2
USERS = [
    ("中国电信", "18000000000", "000000"),
    ("中国移动", "18000000000", "000000"),
    ("中国联通", "18000000000", "000000")
]
ALTCHANNEL = {
    "中国移动": "2",
    "中国电信": "3",
    "中国联通": "4"
}


def GetIP():
    return requests.post(IP, headers=HEADERS, timeout=TIMEOUT).json()["data"]


def PrintIpInfo():
    ret = requests.get(url="https://2021.ip138.com",
                       headers=HEADERS, timeout=TIMEOUT)
    ipurl = re.search(
        r'href="(https://www\.ip138\.com.*?action=\d*)"', ret.content.decode("utf-8")).group(1)
    ipurl = ipurl.replace("&amp;", "&")
    ret = requests.get(url=ipurl, headers=HEADERS, timeout=TIMEOUT)
    ipinfo = re.search(r'var ip_result = (.*?);',
                       ret.content.decode("gb2312")).group(1)
    print("公网 ip:", re.search(r'ip=([\d\.]*?)&', ipurl).group(1))
    print("ASN 归属地:", *json.loads(ipinfo)["ASN归属地"].split())
    print("IP 段:", *json.loads(ipinfo)["iP段"].split())
    print("兼容 IPv6 地址:", *json.loads(ipinfo)["兼容IPv6地址"].split())
    print("映射 IPv6 地址:", *json.loads(ipinfo)["映射IPv6地址"].split())

    print("内网 ip:", GetIP())
    print("")


def Logout():
    data = {
        "username": USERS[0][1],
        "password": USERS[0][2],
        "ifautologin": "0",
        "pagesign": "thirdauth",
        "channel": "0",
        "usripadd": GetIP()
    }
    for key, val in requests.get(url=LOGOUT, data=json.dumps(data).replace(" ", ""), headers=HEADERS, timeout=TIMEOUT).json().items():
        print(f"{key}: {val}")
    print("")


def Login(channel, username, password):
    channel = ALTCHANNEL[channel] if channel in ALTCHANNEL else None
    ip = GetIP()
    data = {
        "channel": channel,
        "ifautologin": "1",
        "pagesign": "secondauth",
        "password": password,
        "username": username,
        "usripadd": ip,
        "ip": ip,
    }
    for key, val in requests.post(url=LOGIN, headers=HEADERS, timeout=TIMEOUT, data=json.dumps(data).replace(" ", "")).json().items():
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
    print("r. 刷新")
    print("w. 注销")
    print("q. 退出")
    print("")


def Run():
    while True:
        CleanScreen()
        try:
            PrintIpInfo()
        except:
            print("获取公网 ip 出错")
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
