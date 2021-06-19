#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import prettytable as pt
import traceback
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
PROXY = {
    # "http": "http://localhost:7890",
    # "https": "http://localhost:7890"
}
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
    "s": ("查看域名 DNS 记录", "ListDomainRecords", [None, True]),
    "x": ("调整域名 DNS 记录", "AdjustDomainRecord", []),
    "h": ("显示菜单", "Menu", []),
    "q": ("退出", "exit", [])
}
DOMAINS = {}
RECORDS = {}
tb = pt.PrettyTable()


def InputNoEmpty(msg=""):
    s = None
    while True:
        s = input(msg).strip()
        if not s:
            print("字符串无效")
        else:
            return s


def CheckProxy():
    if PROXY:
        print("警告：已设置代理")


def CheckAuthInfo():
    if not re.match(r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", CFEMAIL):
        raise Exception("请检查 auth-email")
    if not re.match(r"\w+", CFKEY):
        raise Exception("请检查 auth-key")


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


def REQ(zone, jsonData={}, method="get"):
    method = method.lower()
    ret = getattr(requests, method)(url=ENDPOINTS + zone,
                                    headers=HEADERS, timeout=TIMEOUT, json=jsonData, proxies=PROXY)
    retjson = ret.json()
    if ret.status_code != 200:
        print(ret.status_code, STATUS_CODE[ret.status_code])
        for key, val in retjson.items():
            print("%-20s: %s" % (key, val))
        raise Exception(
            f"请求 \"{ENDPOINTS+zone}\" 时，{STATUS_CODE[ret.status_code]}，详情：{retjson}")
    return retjson["result"]


def GetDomainId(domainName=None):
    for domain in DOMAINS.values():
        if domainName == domain["name"]:
            return domain["id"]
    return ""


def GetRecordId(domainName, recordName=None):
    domainName = CheckDomainName(domainName)
    if not recordName:
        recordName = InputNoEmpty("输入记录名").split()[0]
    if not recordName.endswith("." + domainName):
        recordName += "."+domainName
    domainId = GetDomainId(domainName)
    pendingResult = []
    for record in RECORDS[domainId].values():
        if record["name"] == recordName:
            pendingResult.append(record)
    if len(pendingResult) < 1:
        raise Exception("记录名有误")
    if len(pendingResult) > 1:
        tb.clear()
        tb.field_names = ["index", "type", "name", "content", "proxied", "id"]
        for index, record in enumerate(pendingResult):
            tb.add_row([index, record["type"], record["name"],
                        record["content"], record["proxied"], record["id"]])
        tb.align = "l"
        print(tb)
        choice = InputNoEmpty("有多条记录，输入要修改的记录的编号").split()[0]
        return pendingResult[int(choice)]["id"]
    return pendingResult[0]["id"]


def GetAllDomain():
    global DOMAINS
    domains = REQ("zones", {"per_page": 50, "account.id": ACCOUNTID})
    DOMAINS.clear()
    for domain in domains:
        DOMAINS[domain["id"]] = domain


def GetAllRecord(domainName=None):
    global DOMAINS, RECORDS
    domainName = CheckDomainName(domainName)
    domainId = GetDomainId(domainName)
    RECORDS[domainId] = {}
    print("获取记录中......")
    for record in REQ("zones" + "/" + domainId + "/" + "dns_records", {"per_page": 50}):
        RECORDS[domainId][record["id"]] = record


def CheckDomainName(domainName=None):
    while True:
        if not domainName:
            ListDomains()
            domainName = InputNoEmpty("请输入域名：").split()[0]
        if GetDomainId(domainName):
            return domainName
        else:
            print("没有此域名")
            domainName = None


def ListDomains(domainName=None):
    tb.clear()
    tb.field_names = ["name", "registrar", "status", "id"]
    for domain in DOMAINS.values():
        if not domainName or domainName == domain["id"]:
            tb.add_row(
                [domain["name"], domain["original_registrar"],
                 domain["status"], domain["id"]])
    tb.align = "l"
    print(tb)


def GetRecordInfo(domainName, recordId):
    domainName = CheckDomainName(domainName)
    return RECORDS[GetDomainId(domainName)][recordId]


def PrintRecord(records):
    tb.clear()
    tb.field_names = ["type", "name", "content", "proxied", "id"]
    for record in records:
        tb.add_row([record["type"], record["name"],
                    record["content"], record["proxied"], record["id"]])
    tb.align = "l"
    print(tb)


def ListDomainRecords(domainName=None,  pull=False):
    domainName = CheckDomainName(domainName)
    if pull:
        GetAllRecord(domainName)
    domainName = CheckDomainName(domainName)
    domainId = GetDomainId(domainName)
    PrintRecord(RECORDS[domainId].values())


def GetNewInfo(domainName, recordId=None):
    INPUTMENU = {
        1: ("type", ),
        2: ("name", ),
        3: ("content", ),
        4: ("proxied", ),
    }
    choice = None
    inputFields = []
    _type = None
    _name = None
    _content = None
    _proxied = None
    if domainName and recordId:
        print("原记录为")
        _record = GetRecordInfo(domainName, recordId)
        PrintRecord([_record])
        _type = _record["type"]
        _name = _record["name"]
        _content = _record["content"]
        _proxied = _record["proxied"]
        Menu(INPUTMENU)
        choice = InputNoEmpty("输入要修改的项目的编号").split()[0]
        for ch in choice:
            if int(ch) not in INPUTMENU:
                raise Exception("编号错误")
            inputFields.append(INPUTMENU[int(ch)][0])
    else:
        choice = "1234"
        for field in INPUTMENU.values():
            inputFields.append(field[0])
    print("输入修改后的值")
    print((' '*10).join(inputFields))
    print('-' * 60)
    data = InputNoEmpty().split()
    if len(data) != len(choice):
        raise Exception("数据错误")
    for idx, item in enumerate(data):
        if choice[idx] == '1':
            _type = item
        elif choice[idx] == '2':
            if item != "@" and not item.endswith("." + domainName):
                item += "."+domainName
            _name = item
        elif choice[idx] == '3':
            _content = item
        elif choice[idx] == '4':
            if item.lower() in ['1', 'true']:
                _proxied = True
            else:
                _proxied = False
    return (_type, _name, _content, _proxied)


def AddRecord(domainName=None):
    global RECORDS
    domainName = CheckDomainName(domainName)
    domainId = GetDomainId(domainName)
    [_type, _name, _content, _proxied] = GetNewInfo(domainName)
    print("添加后的记录")
    PrintRecord([{"type": _type, "name": _name,
                  "content": _content, "proxied": _proxied, "id": ""}])
    choice = input("确定要添加吗？")
    if choice in ["", "y", "1"]:
        REQ("zones" + "/" + domainId + "/" + "dns_records",
            {"type": _type, "name": _name, "content": _content, "proxied": _proxied, "ttl": 1}, "POST")
    else:
        print("已取消")


def ChangeRecord(domainName=None):
    domainName = CheckDomainName(domainName)
    domainId = GetDomainId(domainName)
    recordId = GetRecordId(domainName)
    [_type, _name, _content, _proxied] = GetNewInfo(domainName, recordId)
    print("要修改的记录")
    PrintRecord([GetRecordInfo(domainName, recordId)])
    print("修改后的记录")
    PrintRecord([{"type": _type, "name": _name,
                  "content": _content, "proxied": _proxied, "id": ""}])
    choice = input("确定要修改吗？")
    if choice in ["", "y", "1"]:
        REQ("zones" + "/" + domainId + "/" + "dns_records" + "/" + recordId,
            {"type": _type, "name": _name, "content": _content, "proxied": _proxied, "ttl": 1}, "PUT")
    else:
        print("已取消")


def DeleteRecord(domainName=None):
    domainName = CheckDomainName(domainName)
    domainId = GetDomainId(domainName)
    recordId = GetRecordId(domainName)
    print("要删除的记录")
    PrintRecord([GetRecordInfo(domainName, recordId)])
    choice = input("确定要删除吗？")
    if choice in ["", "y", "1"]:
        REQ("zones" + "/" + domainId + "/" + "dns_records" +
            "/" + recordId, {}, "DELETE")
    else:
        print("已取消")


def AdjustDomainRecord():
    domainName = CheckDomainName()
    GetAllRecord(domainName)
    ListDomainRecords(domainName)
    ADJUSTMENU = {
        "a": ("添加记录", "AddRecord", [domainName]),
        "c": ("修改记录", "ChangeRecord", [domainName]),
        "d": ("删除", "DeleteRecord", [domainName]),
        "s": ("查看域名 DNS 记录", "ListDomainRecords", [domainName]),
        "q": ("返回上一层", "",)
    }
    ADJUSTMENU["h"] = ("显示菜单", "Menu", [ADJUSTMENU])
    Menu(ADJUSTMENU)
    while True:
        print("当前域名：%s" % domainName)
        choice = InputNoEmpty("二级菜单，请输入命令").split()[0]
        if choice == "q":
            break
        if choice in ADJUSTMENU:
            print("您选择了 %s：%s" % (choice, ADJUSTMENU[choice][0]))
            try:
                eval(ADJUSTMENU[choice][1])(*ADJUSTMENU[choice][2])
            except Exception:
                print(traceback.format_exc())
            GetAllRecord(domainName)
            ListDomainRecords(domainName)
        else:
            print("命令 %s 不存在" % choice)


def Run():
    choice = InputNoEmpty("一级菜单，请输入命令").split()[0]
    if choice in MENU:
        print("您选择了 %s：%s" % (choice, MENU[choice][0]))
        try:
            eval(MENU[choice][1])(*MENU[choice][2])
        except Exception:
            print(traceback.format_exc())
    else:
        print("命令 %s 不存在" % choice)


def Init():
    print("初始化......")
    CheckProxy()
    CheckAuthInfo()
    SetAccountId()
    GetAllDomain()


if __name__ == "__main__":
    try:
        Init()
        ListDomains()
        Menu()
        while True:
            Run()
    except KeyboardInterrupt:
        pass
    except BaseException:
        print(traceback.format_exc())
