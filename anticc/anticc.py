#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from config import *
import subprocess
import traceback
import sys
import os
import re
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def system(command, log=True):
    if DEBUG:
        print(command)
    p = subprocess.Popen(command, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    msg = p.stdout.read().decode("utf-8") + "\n" + p.stderr.read().decode("utf-8")
    status = p.returncode
    if status < 0:
        raise Exception(f"执行命令失败：{command}")
    if log:
        AddLog("[command]\ncommand: " + command +
               "\nstatus: " + str(status) + "\nmsg: " + msg)
    return (status, msg)


def AddLog(content):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FOLDER + LOG_NAME, "ab") as fo:
        fo.write((t + " " + str(content) + "\n").encode("utf-8"))


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
    AddLog("[mail]\nsubject: " + subject + "\ncontent: " + content)


def CheckIpFormat(ip):
    if DEBUG:
        print(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
    if len(ip) < 7 or not re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip):
        print(ip + " 不合法，请输入正确的 ip")
        return False
    else:
        return True


def CheckIpset():
    ret = system(f"{IPSET} list -name", False)
    if ret[1].find(IPSET_NAME) == -1:
        InitIpset()
    ret = system(f"{IPTABLES} -nL", False)
    if ret[1].find(f"match-set {IPSET_NAME}") == -1:
        InitIpset()


def InitIpset():
    system(f"{IPTABLES} -D INPUT -p tcp -m set --match-set {IPSET_NAME} src -j DROP")
    system(f"{IPSET} destroy {IPSET_NAME}")
    system(f"{IPSET} restore -file {SCRIPT_FOLDER}{IPSET_SAVE_NAME}")
    ret = system(f"{IPTABLES} -nL")
    if ret[1].find(f"match-set {IPSET_NAME}") != -1:
        raise Exception(
            "iptables 疑似规则重复，尝试使用 iptables -D INPUT -p tcp -m set --match-set anticc src -j DROP")
    system(f"{IPTABLES} -I INPUT -p tcp -m set --match-set {IPSET_NAME} src -j DROP")


def RemoveCron():
    if CRON_NAME in os.listdir(CRON_FOLDER):
        os.remove(CRON_FOLDER + CRON_NAME)
        system(f"{SERVICE} crond restart")


def AddCron():
    with open(CRON_FOLDER + CRON_NAME, "wb") as fo:
        fo.write(CRON_CONTENT.encode("utf-8"))
    system(f"{SERVICE} cron restart")


def SaveIpset():
    system(f"{IPSET} save {IPSET_NAME} -file {SCRIPT_FOLDER}{IPSET_SAVE_NAME}")


def ReleaseIp(ip):
    if (DEBUG):
        print(ip)
    ret = system(f"{IPSET} del {IPSET_NAME} {ip}")
    if ret[0] == 0:
        print(f"{ip} 已释放")
    else:
        print(f"{ip} 未被屏蔽，请检查拼写")


def BanIp(ip):
    if (DEBUG):
        print(ip)
    ret = system(f"{IPSET} add {IPSET_NAME} {ip}")
    if ret[0] == 0:
        print(f"{ip} 已屏蔽")
    else:
        print(f"{ip} 已被屏蔽过，跳过")
    return ret[0]


def Run(Max_Connection):
    mailList = []
    CheckIpset()
    with open(SCRIPT_FOLDER + WHITE_LIST, "rb") as fi:
        whiteList = [i.decode('utf-8').rstrip() for i in fi.readlines()]
        if DEBUG:
            print(whiteList)
    ret = system(
        "netstat -ntu | tail -n+3 | awk '{print $5}' | grep -v :: | cut -d: -f1 | sort | uniq -c | sort -nr")
    print(ret[1])
    for line in ret[1].split("\n"):
        if len(line.strip()) == 0:
            continue
        [connection, ip] = line.split()
        connection = int(connection)
        if connection >= Max_Connection:
            if ip in whiteList:
                print(f"{ip} 在白名单中，跳过")
            elif BanIp(ip) == 0:
                mailList.append(f"{ip}：{connection} 连接")
        else:
            break
    ret = system("top -bn 1 |grep Cpu | cut -d \".\" -f 1 | cut -d \":\" -f 2")
    cpuload = int(ret[1])
    print(f"CPU 负载 {cpuload}%")
    if len(mailList) > 0:
        if cpuload > 70:
            mailList.append(f"CPU 负载 {cpuload}%，已运行恢复命令")
            for cmd in RECOVERY_CODE:
                if cmd == 0:
                    time.sleep(5)
                    continue
                system(cmd)
        SaveIpset()
        SendMail(f"在主机 {LOCAL_NAME} 上发现 CC 攻击",
                 f"在主机 {LOCAL_NAME} 上发现 CC 攻击，当前阈值 {Max_Connection}，以下攻击 IP 已屏蔽：\n"+"\n".join(mailList))


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This program must be run as root. Aborting.")
        exit(1)
    try:
        if len(sys.argv) > 1:
            argv = sys.argv[1]
            if argv == "rel":
                if len(sys.argv) <= 2:
                    raise Exception("请输入 ip")
                for ip in sys.argv[2:]:
                    if CheckIpFormat(ip):
                        ReleaseIp(ip)
                SaveIpset()
            elif argv == "ban":
                if len(sys.argv) <= 2:
                    raise Exception("请输入 ip")
                for ip in sys.argv[2:]:
                    if CheckIpFormat(ip):
                        BanIp(ip)
                SaveIpset()
            elif argv == "cron":
                AddCron()
            elif argv == "rmcron":
                RemoveCron()
            elif argv == "init":
                InitIpset()
            elif argv.isdigit():
                Run(int(argv))
            else:
                print("未知的参数")
            exit()
        Run(MAX_CONNECTION)
    except Exception as e:
        s = traceback.format_exc()
        AddLog(s)
        SendMail(f"在主机 {LOCAL_NAME} 上执行 {SCRIPT_NAME} 时发生错误",
                 f"在主机 {LOCAL_NAME} 上执行 {SCRIPT_NAME} 时发生错误，错误内容如下\n{s}")
        raise e
