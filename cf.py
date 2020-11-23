#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
CFEMAIL = "ac@qq.com"
CFKEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ACCOUNTID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ENDPOINTS = "https://api.cloudflare.com/client/v4/"
HEADERS = {
    "Content-Type": "application/json",
    "X-Auth-Key": CFKEY,
    "X-Auth-Email": CFEMAIL
}
# PROXY = {
#     "http": "http://localhost:7890",
#     "https": "http://localhost:7890"
# }
TIMEOUT = 5
STATUS_CODE = {
    200: "OK",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    429: "Too many requests",
    405: "Method Not Allowed",
    415: "Unsupported Media Type"
}
MENU = {
    "u": ("显示用户信息", "ShowUserInfo", []),
    "a": ("显示账户信息", "ShowAccountInfo", []),
    "l": ("查看域名列表", "ListDomains", []),
    "s": ("查看域名 DNS 记录", "ListDomainRecords", []),
    "x": ("调整域名 DNS 记录", "AdjustDomainRecord", []),
    "h": ("显示菜单", "Menu", []),
    "q": ("退出", "exit", [])
}
DOMAINS = {}
RECORDS = {}


def CheckAuthInfo():
    if not re.match(r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", CFEMAIL):
        raise Exception("请检查 auth-email")
    if not re.match(r"\w+", CFKEY):
        raise Exception("请检查 auth-key")


def REQ(zone, jsonData={}, method="get"):
    method = method.lower()
    ret = getattr(requests, method)(url=ENDPOINTS + zone,
                                    headers=HEADERS, timeout=TIMEOUT, json=jsonData)
    # ret = getattr(requests, method)(url=ENDPOINTS + zone,
    #                                 headers=HEADERS, timeout=TIMEOUT, json=jsonData, proxies=PROXY)
    retjson = ret.json()
    if ret.status_code != 200:
        print(ret.status_code, STATUS_CODE[ret.status_code])
        for key, val in retjson.items():
            print("%-20s: %s" % (key, val))
        raise Exception(
            f"请求 \"{ENDPOINTS+zone}\" 时，{STATUS_CODE[ret.status_code]}")
    return retjson["result"]


def SetAccountId():
    global ACCOUNTID
    if len(ACCOUNTID) == 0:
        ACCOUNTID = REQ("accounts")[0]["id"]


def ShowUserInfo():
    for key, val in REQ("user").items():
        print("%-20s: %s" % (key, val))


def ShowAccountInfo():
    for key, val in REQ("accounts")[0].items():
        print("%-20s: %s" % (key, val))


def Menu(menu=MENU):
    for key, val in menu.items():
        print("%2s. %s" % (key, val[0]))


def ListDomains():
    global DOMAINS
    domains = REQ("zones", {"per_page": 50, "account.id": ACCOUNTID})
    print("%-15s %-10.10s %-10s %-35s" %
          ("name", "registrar", "status", "id",))
    print("-" * 60)
    for domain in domains:
        print("%-15s %-10.10s %-10s %-35s" %
              (domain["name"], domain["original_registrar"], domain["status"], domain["id"]))
        DOMAINS[domain["name"]] = domain["id"]


def ListDomainRecords(domainName=""):
    global DOMAINS, RECORDS
    if domainName == "":
        domainName = input("请输入域名：").split()[0]
    domainId = ""
    if domainName not in DOMAINS:
        domains = REQ("zones", {"per_page": 50,
                                "account.id": ACCOUNTID, "name": domainName})
        for domain in domains:
            DOMAINS[domain["name"]] = domain["id"]
    if domainName in DOMAINS:
        domainId = DOMAINS[domainName]
    else:
        raise Exception("您名下没有此域名：%s" % domainName)
    print("%-10s %-20s %-20s %-35s" % ("type", "name", "content", "id"))
    print("-" * 60)
    RECORDS[domainName] = {}
    for record in REQ("zones" + "/" + domainId + "/" + "dns_records", {"per_page": 50}):
        print("%-10s %-20s %-20s %-35s" %
              (record["type"], record["name"], record["content"], record["id"]))
        RECORDS[domainName][record["name"]] = {
            "type": record["type"], "content": record["content"], "id": record["id"]}
    return domainName


def AddRecord(domainName=""):
    global RECORDS
    if domainName == "":
        domainName = input("请输入域名：").split()[0]
    print("请输入记录的 type、name、content")
    print("%-10s %-20s %-20s" % ("type", "name", "content"))
    recordType, recordName, recordContent = input().split()
    recordType = recordType.upper()
    if recordName in RECORDS[domainName]:
        print("原记录已存在，你确定要添加吗？原记录如下：")
        print("%-10s %-20s %-20s %-35s" % ("type", "name", "content", "id"))
        print("-" * 60)
        print("%-10s %-20s %-20s %-35s" % (RECORDS[domainName][recordName]["type"], recordName,
                                           RECORDS[domainName][recordName]["content"], RECORDS[domainName][recordName]["id"]))
    print("你确定要添加以下记录吗？（y/n）")
    print("%-10s %-20s %-20s" % ("type", "name", "content"))
    print("-" * 60)
    print("%-10s %-20s %-20s" % (recordType, recordName, recordContent))
    choice = input()
    if choice == "y" or choice == "":
        domainId = DOMAINS[domainName]
        record = REQ("zones" + "/" + domainId + "/" + "dns_records",
                     {"type": recordType, "name": recordName, "content": recordContent, "ttl": 1}, "POST")
        print("以下记录添加成功：")
        print("%-10s %-20s %-20s %-35s" % ("type", "name", "content", "id"))
        print("-" * 60)
        print("%-10s %-20s %-20s %-35s" %
              (record["type"], record["name"], record["content"], record["id"]))
        RECORDS[domainName][record["name"]] = {
            "type": record["type"], "content": record["content"], "id": record["id"]}
    else:
        print("已取消")


def ChangeRecord(domainName=""):
    if domainName == "":
        domainName = input("请输入域名：").split()[0]
    print("请输入记录的 type、name、content")
    print("%-10s %-20s %-20s" % ("type", "name", "content"))
    recordType, recordName, recordContent = input().split()
    recordType = recordType.upper()
    if recordName not in RECORDS[domainName]:
        print("原纪录不存在，无法修改")
        return
    print("原记录已存在，你确定要修改吗？原记录如下：")
    print("%-10s %-20s %-20s %-35s" % ("type", "name", "content", "id"))
    print("-" * 60)
    print("%-10s %-20s %-20s %-35s" % (RECORDS[domainName][recordName]["type"], recordName,
                                       RECORDS[domainName][recordName]["content"], RECORDS[domainName][recordName]["id"]))
    print("你确定要将原纪录修改为以下记录吗？（y/n）")
    print("%-10s %-20s %-20s" % ("type", "name", "content"))
    print("-" * 60)
    print("%-10s %-20s %-20s" % (recordType, recordName, recordContent))
    choice = input()
    if choice == "y" or choice == "":
        domainId = DOMAINS[domainName]
        record = REQ("zones" + "/" + domainId + "/" + "dns_records" + "/" + RECORDS[domainName][recordName]["id"],
                     {"type": recordType, "name": recordName, "content": recordContent, "ttl": 1}, "PUT")
        print("已修改为以下记录：")
        print("%-10s %-20s %-20s %-35s" % ("type", "name", "content", "id"))
        print("-" * 60)
        print("%-10s %-20s %-20s %-35s" %
              (record["type"], record["name"], record["content"], record["id"]))
        RECORDS[domainName][record["name"]] = {
            "type": record["type"], "content": record["content"], "id": record["id"]}
    else:
        print("已取消")


def DeleteRecord(domainName=""):
    if domainName == "":
        domainName = input("请输入域名：").split()[0]
    print("请输入记录的 name")
    print("%-20s" % "name")
    recordName = input().split()[0]
    if recordName not in RECORDS[domainName]:
        print("原纪录不存在，无法删除")
        return
    print("原记录已存在，你确定要删除吗？原记录如下：")
    print("%-10s %-20s %-20s %-35s" % ("type", "name", "content", "id"))
    print("-" * 60)
    print("%-10s %-20s %-20s %-35s" % (RECORDS[domainName][recordName]["type"], recordName,
                                       RECORDS[domainName][recordName]["content"], RECORDS[domainName][recordName]["id"]))
    print("你确定要删除吗？（y/n）")
    choice = input()
    if choice == "y" or choice == "":
        domainId = DOMAINS[domainName]
        record = REQ("zones" + "/" + domainId + "/" + "dns_records" +
                     "/" + RECORDS[domainName][recordName]["id"], {}, "DELETE")
        print("已删除以下记录：")
        print("%-35s" % "id")
        print("-" * 60)
        print("%-35s" % record["id"])
        del RECORDS[domainName][recordName]
    else:
        print("已取消")


def AdjustDomainRecord():
    domainName = ListDomainRecords()
    ADJUSTMENU = {
        "a": ("添加记录", "AddRecord", [domainName]),
        "c": ("修改记录", "ChangeRecord", [domainName]),
        "d": ("删除", "DeleteRecord", [domainName]),
        "s": ("查看域名 DNS 记录", "ListDomainRecords", [domainName]),
        "q": ("返回上一层", "",)
    }
    Menu(ADJUSTMENU)
    while True:
        print("请输入命令")
        choice = input().split()[0]
        if choice == "q":
            break
        if choice in ADJUSTMENU:
            print("您选择了 %s：%s" % (choice, ADJUSTMENU[choice][0]))
            eval(ADJUSTMENU[choice][1])(*ADJUSTMENU[choice][2])
        else:
            print("命令 %s 不存在" % choice)


def Run():
    print("请输入命令，输入 h 查看菜单")
    choice = input().split()[0]
    if choice in MENU:
        print("您选择了 %s：%s" % (choice, MENU[choice][0]))
        eval(MENU[choice][1])(*MENU[choice][2])
    else:
        print("命令 %s 不存在" % choice)


if __name__ == "__main__":
    try:
        CheckAuthInfo()
        SetAccountId()
        Menu()
        while True:
            Run()
    except KeyboardInterrupt as e:
        pass
    except BaseException as e:
        print(repr(e))
