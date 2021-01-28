# -*- codeing = utf-8 -*-
# @Time : 2021/1/26 22:25
# @Author : 96bearli
# @File : main.py
# @Software : PyCharm
'''
思路       从github拉取proxylist，本地验活后保存为txt文档
文档包含    http/https,ip:port,ping
验证方法    requests.get(url="http://icanhazip.com/", proxies=Proxy)
使用多线程加快速度
type可选
即将增加的功能 去重
'''
import telnetlib
import requests
import re
import queue
import threading

# 获取代理信息的格式模板
# 文档要求: 1.一行一条，可以有无效行
#          2.需要utf-8编码才能使通用提取函数生效（大概）
# 文档url+模式+匹配ip规则+匹配端口规则+匹配模式规则
# 当type不固定时对应"mix",且默认使用的的telnet不支持ss4/ss5
# 有需求可以自行修改checkProxy()
# raw1 = {"url": 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
#         "type": "mix",
#         "findIp": re.compile(r'"host": "(.+?)"'),
#         "findPort": re.compile(r'"port": (\d+?),'),
#         "findType": re.compile(r'"type": "(.+?)"')}

# raw1_mix
# {"host": "3.211.65.185", "from": "proxylist", "country": "US", "port": 80, "response_time": 0.82, "export_address": ["35.193.184.18", "192.168.99.102", "54.226.33.176"], "type": "http", "anonymity": "high_anonymous"}
raw1 = {"url": 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
        "type": "mix",
        "findIp": re.compile(r'"host": "(.+?)"'),
        "findPort": re.compile(r'"port": (\d+?),'),
        "findType": re.compile(r'"type": "(.+?)"')}
# raw2_http
# 62.171.170.82:3128
raw2 = {"url": 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
        "type": "http",
        "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
        "findPort": re.compile(r':(\d+?)\n'),
        "findType": ""}
# raw3_http
# 62.171.170.82:3128
raw3 = {"url": 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
        "type": "http",
        "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
        "findPort": re.compile(r':(\d+?)\n'),
        "findType": ""}
# raw4_http
# 178.212.54.137:8080
raw4 = {"url": 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        "type": "http",
        "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
        "findPort": re.compile(r':(\d+?)\n'),
        "findType": ""}

# raw5_https
# 103.21.161.105:6667
raw5 = {"url": 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
        "type": "https",
        "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
        "findPort": re.compile(r':(\d+?)\n'),
        "findType": ""}
# raw6_HTTP/HTTPS
# 203.202.245.58:80
raw6 = {"url": 'https://sunny9577.github.io/proxy-scraper/proxies.txt',
        "type": "https",
        "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
        "findPort": re.compile(r':(\d+?)\n'),
        "findType": ""}
raws = [raw1, raw2, raw3, raw4, raw5]

# 镜像，按需替换链接
# 内地cdn
# proxyListUrl = 'https://raw.sevencdn.com/fate0/proxylist/master/proxy.list'
# proxyListUrl = 'https://cdn.jsdelivr.net/gh/fate0/proxylist@master/proxy.list'
# 香港cdn
# proxyListUrl = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'


def checkProxy():
    # 当队列不为空时
    while not checkDataQueue.empty():
        # 从队列读取一条数据
        # 读取是阻塞操作
        proxies = checkDataQueue.get()
        ip = proxies[0]
        port = proxies[1]
        type = proxies[2]
        Proxy = type + '://' + ip + ':' + port
        print(Proxy)
        try:
            '''requests方法
            rep = requests.get(url="http://icanhazip.com/", timeout=3, proxies={type: Proxy})
            repIp = rep.text.replace("\n", "")
            if repIp == ip:
            '''

            # 换成telnet的方式更合适
            telnetlib.Telnet(ip, port=port, timeout=3)

            # 在这里选择type
            if type == "http":
                print("找到一条有效代理 %s" % Proxy)
                # 申请获取锁，此过程为阻塞等待状态，直到获取锁完毕
                mutex_lock.acquire()
                with open('./proxy1.txt', 'a+', encoding='utf-8') as f:
                    f.write(Proxy + "\n")
                mutex_lock.release()
            else:
                print("无效")
        except Exception as proxyError:
            print(proxyError)
            print("无效")


def getProxyList():
    allList = []

    for raw in raws:
        # print(raw["type"])
        try:
            response = requests.get(raw["url"])
            print(response.content)
        except Exception as rawError:
            print(rawError)
            input("raw%i已失效，请检查，按任意键继续" % (raws.index(raw)+1))
            continue
        # 分割双保险
        try:
            print("尝试.split('\\n')分割")
            # \n分割
            theList = response.content.split('\n')
        except:
            # 用re正则提取单条数据
            print("尝试正则分割")
            findLine = re.compile(r".+?\n")
            theList = re.findall(findLine, response.text)
        # 提取数据
        if raw["type"] != "mix":
            for line in theList:
                line = str(line)
                try:
                    ip = re.findall(raw["findIp"], line)[0]
                    port = re.findall(raw["findPort"], line)[0]
                    type = raw["type"]
                    aList = [ip, port, type]
                    allList.append(aList)
                except Exception as reError:
                    print(reError)
                    continue
        else:
            for line in theList:
                line = str(line)
                try:
                    ip = re.findall(raw["findIp"], line)[0]
                    port = re.findall(raw["findPort"], line)[0]
                    type = re.findall(raw["findType"], line)[0]
                    aList=[ip, port, type]
                    allList.append(aList)
                except Exception as reError:
                    print(reError)
                    continue
    # 测试点
    # with open("./cache", "w") as f:
    #     for all in allList:
    #         for a in all:
    #             f.write(a)
    #         f.write("\n")
    return allList


if __name__ == '__main__':
    # 先拿到要处理的代理数据列表
    proxiesList = getProxyList()
    # 将所有代理数据列表放入先进先出FIFO队列中
    # 队列的写入和读取都是阻塞的，故在多线程情况下不会乱
    # 在不使用框架的前提下，引入多线程，提高爬取效率
    # 创建一个队列
    checkDataQueue = queue.Queue(len(proxiesList))
    # 写入代理数据到队列
    for proxy in proxiesList:
        # proxiesList[i]也是list类型，分别存入队列
        checkDataQueue.put(proxy)
    # 创建一个线程锁，防止多线程写入文件时发生错乱
    mutex_lock = threading.Lock()
    # 线程数为15，在一定范围内，线程数越多，速度越快
    for i in range(140):
        t = threading.Thread(target=checkProxy, name='LoopThread' + str(i))
        t.start()

    # readPath = 'proxy1.txt'
    # writePath = 'proxy.txt'
    # lines_seen = set()
    # outfiile = open(writePath, 'a+', encoding='utf-8')
    # f = open(readPath, 'r', encoding='utf-8')
    # for line in f:
    #     if line not in lines_seen:
    #         outfiile.write(line)
    #         lines_seen.add(line)
