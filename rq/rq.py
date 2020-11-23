#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from getopt import getopt, GetoptError

DEBUG = False
USEOLDQID = True
USEOLDCOOKIES = True
USER = "******"
PASS = "**********"
QQ = "*********"
INDEXURL = "https://www.qqzzz.net/www/index.php?mod=login"
LOGINURL = f"https://www.qqzzz.net/www/index.php?my=login&user={USER}&pass={PASS}&ctime=2592000"
USERHOME = "https://www.qqzzz.net/www/index.php?mod=user"
PIDPAGE = f"https://www.qqzzz.net/www/index.php?mod=rq&qq={QQ}"
RPURL = "https://www.qqzzz.net/www/qq/api/rq.php"
HEADERS = {
    "user-agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "accept": r"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Connection": r"close"
}
MAINFOLDER = os.path.dirname(os.path.realpath(__file__)) + "/"
COOKIESFILE = "cookies.txt"
QIDFILE = "qid.txt"
INTERVAL = 0.8
TIMEOUT = 2
ATK = 300

LOCAL_NAME = "本地"
EMAIL_HOST = "smtp.qq.com"
EMAIL_PORT = 465
EMAIL_FROM = "*****@foxmail.com"
EMAIL_FROM_NAME = "*****"
EMAIL_PASS = "*************"
EMAIL_TO = "*****@qq.com"
EMAIL_TO_NAME = "*****"


def SendMail(subject, content):
    if (DEBUG):
        print("主题："+subject)
        print("内容："+content)
    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = formataddr([EMAIL_FROM_NAME, EMAIL_FROM])
    msg["To"] = formataddr([EMAIL_TO_NAME, EMAIL_TO])
    msg["Subject"] = subject
    server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
    server.login(EMAIL_FROM, EMAIL_PASS)
    server.sendmail(EMAIL_FROM, [EMAIL_TO, ], msg.as_string())
    server.quit()


def GetSESSIONID():
    ret = requests.post(INDEXURL, headers=HEADERS, timeout=TIMEOUT)
    if DEBUG:
        print(ret.content.decode("utf-8"))
    print("获取了 SESSIONID")
    return requests.utils.dict_from_cookiejar(ret.cookies)


def GetCookiesByLogin():
    ret = requests.get(url=LOGINURL, headers=HEADERS, timeout=TIMEOUT)
    if DEBUG:
        print(ret.content.decode("utf-8"))
    cookies = requests.utils.dict_from_cookiejar(ret.cookies)
    if TestCookieVaild(cookies):
        print("通过登录获取了 cookies")
        return cookies
    else:
        raise Exception("获取 cookies 失败")


def GetVaildCookies():
    if USEOLDCOOKIES and COOKIESFILE in os.listdir(MAINFOLDER):
        with open(MAINFOLDER + COOKIESFILE, "rb") as fi:
            cookies = {}
            for line in [i.decode("utf-8").rstrip() for i in fi.readlines()]:
                [key, val] = line.split("=")
                cookies[key] = val
        if TestCookieVaild(cookies):
            print("使用了已有 cookies")
            return cookies
        print("已有 cookies 失效")
    cookies = GetCookiesByLogin()
    with open(MAINFOLDER + COOKIESFILE, "wb") as fo:
        for key, val in cookies.items():
            fo.write(f"{key}={val}\n".encode("utf-8"))
    print("使用了新 cookies")
    print("获取了合法 cookies")
    return cookies


def TestCookieVaild(cookies):
    ret = requests.get(url=USERHOME, headers=HEADERS,
                       cookies=cookies, timeout=TIMEOUT)
    if DEBUG:
        print(ret.content.decode("utf-8"))
    if ret.content.decode("utf-8").find(USER) != -1:
        return True
    else:
        return False


def GetPidByGet(cookies):
    ret = requests.get(url=PIDPAGE, headers=HEADERS,
                       cookies=cookies, timeout=TIMEOUT)
    lis = []
    for match in re.finditer("qid=\"(\\d*)\"", ret.content.decode("utf-8")):
        lis.append(match.group(1))
    if DEBUG:
        print(lis)
    print(f"通过网页获取了 {len(lis)} 个新 qid")
    return lis


def GetVaildPid(cookies):
    qidSet = set()
    if USEOLDQID and QIDFILE in os.listdir(MAINFOLDER):
        with open(MAINFOLDER + QIDFILE, "rb") as fi:
            for line in [i.decode("utf-8").rstrip() for i in fi.readlines()]:
                qidSet.add(line)
        print("读取了已有 pid")
    count = 0
    while len(qidSet) < ATK and count < 5:
        qidSet.update(GetPidByGet(cookies))
        print("获取了新 qid")
        count += 1
        time.sleep(INTERVAL)
    # while len(qidSet) > ATK:
        # qidSet.pop()
    print(f"获取了 {len(qidSet)} 个 qid")
    SaveQidToFile(list(qidSet))
    return list(qidSet)


def SaveQidToFile(qidList):
    with open(MAINFOLDER + QIDFILE, "wb") if USEOLDQID else open(MAINFOLDER + QIDFILE, "ab") as fo:
        for qid in qidList:
            fo.write((qid+"\n").encode("utf-8"))
    print(f"保存了 {len(qidList)} 个 pid")


def Run():
    try:
        cookies = GetVaildCookies()
    except Exception as e:
        SendMail(f"在 {LOCAL_NAME} 上运行 人气 脚本时出错", "获取 cookies 失败，请检查网络")
        raise e
    vaildQid = []
    qidList = GetVaildPid(cookies)
    count = 0
    for qid in qidList:
        if count >= ATK:
            break
        body = {
            "uin": QQ,
            "qid": qid
        }
        error = False
        count += 1
        try:
            ret = requests.post(url=RPURL, data=body, headers=HEADERS,
                                cookies=cookies, timeout=TIMEOUT)
        except KeyboardInterrupt as e:
            raise e
        except:
            error = True
        if not error and ret.status_code != 200 or ret.content.decode("utf-8").find("刷人气成功") == -1:
            print(f"{count}: qid {qid} 刷人气失败")
            continue
        if DEBUG:
            print(ret.content.decode("utf-8"))
        vaildQid.append(qid)
        print(f"{count}: qid {qid} 刷人气成功")
        time.sleep(INTERVAL)
    print(f"共计刷人气 {len(vaildQid)} 次")
    vaildQid.extend(qidList[count:])
    SaveQidToFile(vaildQid)


def solveArgs():
    global QQ, DEBUG, INTERVAL, ATK
    try:
        opts = getopt(sys.argv[1:], "dq:i:n:")[0]
    except GetoptError:
        print("请输入正确参数")
        print("rq.py [-d] [-q 123456789] [-i 0.5] [-n 500]")
        sys.exit(1)
    if DEBUG:
        print(opts)
    for key, val in opts:
        if key == "-d":
            DEBUG = True
        elif key == "-q":
            if not val.isdigit() or len(val) > 10:
                print("请输入正确参数")
                print("rq.py [-d] [-q 123456789] [-i 0.5] [-n 500]")
                sys.exit(1)
            QQ = val
        elif key == "-i":
            INTERVAL = float(val)
        elif key == "-n":
            ATK = int(val)
    print(f"是否开启 DEBUG：{DEBUG}")
    print(f"当前 QQ：{QQ}")
    print(f"当前间隔：{INTERVAL}s")
    print(f"当前 ATK：{ATK}")


try:
    solveArgs()
    Run()
    print("运行完成")
except Exception as e:
    raise e
