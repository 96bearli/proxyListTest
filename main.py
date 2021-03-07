# -*- codeing = utf-8 -*-
# @Time : 2021/1/26 22:25
# @Author : 96bearli
# @File : main.py
# @Software : PyCharm
'''
思路       从github拉取proxylist，本地验活后保存为txt文档
文档包含    http/https,ip:port,ping
验证方法    requests.get(url="http://icanhazip.com/", proxies=Proxy)>划掉但仍可选，并发应减少到个位
          默认 telnet验证
使用多线程加快速度
type可选 在checkProxy()    if "http" in type:  处修改
即将增加的功能 去重>已增加
更改：采用双重验证方法获取高质量稳定代理（比如2500筛选100）
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
# raw = {"url": 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
#        "type": "mix",
#        "findIp": re.compile(r'"host": "(.+?)"'),
#        "findPort": re.compile(r'"port": (\d+?),'),
#        "findType": re.compile(r'"type": "(.+?)"')}
# raws.append(raw)
raws = []
# raw1_mix
# {"host": "3.211.65.185", "from": "proxylist", "country": "US", "port": 80, "response_time": 0.82, "export_address": ["35.193.184.18", "192.168.99.102", "54.226.33.176"], "type": "http", "anonymity": "high_anonymous"}
raw = {"url": 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
       "type": "mix",
       "findIp": re.compile(r'"host": "(.+?)"'),
       "findPort": re.compile(r'"port": (\d+?),'),
       "findType": re.compile(r'"type": "(.+?)"')}
raws.append(raw)
# raw2_http
# 62.171.170.82:3128
raw = {"url": 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
       "type": "http",
       "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
       "findPort": re.compile(r':(\d+?)\n'),
       "findType": ""}
raws.append(raw)
# raw3_http
# 62.171.170.82:3128
raw = {"url": 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
       "type": "http",
       "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
       "findPort": re.compile(r':(\d+?)\n'),
       "findType": ""}
raws.append(raw)
# raw4_http
# 178.212.54.137:8080
raw = {"url": 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
       "type": "http",
       "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
       "findPort": re.compile(r':(\d+?)\n'),
       "findType": ""}
raws.append(raw)
# raw5_https
# 103.21.161.105:6667
raw = {"url": 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
       "type": "https",
       "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
       "findPort": re.compile(r':(\d+?)\r\n'),
       "findType": ""}
raws.append(raw)
# raw6_HTTP/HTTPS
# 203.202.245.58:80
raw = {"url": 'https://sunny9577.github.io/proxy-scraper/proxies.txt',
       "type": "https",
       "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
       "findPort": re.compile(r':(\d+?)\n'),
       "findType": ""}
raws.append(raw)


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
            # 尝试使用telnet和req结合的双重验证
            telnetlib.Telnet(ip, port=port, timeout=3)
            # 在这里选择type，in筛选http/https。not in 或其他
            # if "http" in type:
            if type == "http":
                rep = requests.get(url="http://icanhazip.com/", timeout=3, proxies={type: Proxy})
                repIp = str(rep.text.replace("\n", ""))
                if repIp in Proxy:
                    print("双重验证后找到一条较高质量的代理,%s" % Proxy)
                    # 申请获取锁，此过程为阻塞等待状态，直到获取锁完毕
                    mutex_lock.acquire()
                    with open('./proxy.txt', 'a+', encoding='utf-8') as file:
                        file.write(Proxy+'\n')
                    mutex_lock.release()

            # 纯requests方法
            # rep = requests.get(url="http://icanhazip.com/", timeout=3, proxies={type: Proxy})
            # repIp = rep.text.replace("\n", "")
            # if repIp == ip:
            #     if type == "http":
            #         print("找到一条有效代理 %s" % Proxy)
            #         # 申请获取锁，此过程为阻塞等待状态，直到获取锁完毕
            #         mutex_lock.acquire()
            #         with open('./proxy.txt', 'a+', encoding='utf-8') as f:
            #             f.write(Proxy + "\n")
            #         mutex_lock.release()
            #     else:
            #         print("无效")

            # 纯telnet的方式
            # telnetlib.Telnet(ip, port=port, timeout=3)
            # # 在这里选择type，in筛选http/https。not in 其他，并自行修改检查方式为requests
            # # if "http" in type:
            # if type == "http":
            #     print("找到一条有效代理 %s" % Proxy)
            #     # 申请获取锁，此过程为阻塞等待状态，直到获取锁完毕
            #     mutex_lock.acquire()
            #     with open('./proxy.txt', 'a+', encoding='utf-8') as f:
            #         f.write(Proxy + "\n")
            #     mutex_lock.release()
            # else:
            #     print("无效")

        except Exception as proxyError:
            print(proxyError)
            print("无效")


def reWriteList(aList):
    # 刚开始想直接list(set(list)),报错列表不能哈希，查了一下二维列表需要先转元组
    aList = list(set([tuple(t) for t in aList]))
    return aList


def getProxyList():
    allList = []
    for raw in raws:
        print("-" * 20)
        print("正在尝试获取源raw%i提供的列表" % (raws.index(raw) + 1))
        try:
            response = requests.get(raw["url"], timeout=3)
            print(response.content)
        except Exception as rawError:
            print(rawError)
            try:  # 尝试自动更换镜像
                response = requests.get(raw["url"].replace("raw.githubusercontent.com", "raw.sevencdn.com"), timeout=3)
                print(response.content)
                print("raw%i原始地址尝试失败，自动更换镜像地址成功" % (raws.index(raw) + 1))
            except Exception as rawError2:
                print(rawError2)
                input("raw%i_url已失效，请检查，可尝试自行更换，按回车继续" % (raws.index(raw) + 1))
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
                    aList = [ip, port, type]
                    allList.append(aList)
                except Exception as reError:
                    print(reError)
                    continue
    # 去重+统计
    from time import sleep
    before = len(allList)
    if before == 0:
        print("还是好好检查一下源的配置吧")
        exit()
    allList = reWriteList(allList)
    after = len(allList)
    print("-" * 20)
    print("本次运行获取代理数据%i条，去重复后剩余%i条" % (before, after))
    print("3秒后自动开始多进程验活")
    print("-" * 20)
    sleep(3)
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
    # 创建空文件./proxy.txt
    with open('./proxy.txt', 'w', encoding='utf-8') as f:
        pass
    # 将所有代理数据列表放入先进先出FIFO队列中
    # 队列的写入和读取都是阻塞的，故在多线程情况下不会乱
    # 在不使用框架的前提下，引入多线程，提高爬取效率
    # 创建一个队列
    checkDataQueue = queue.Queue(len(proxiesList))
    # 写入代理数据到队列
    for proxy in proxiesList:
        # proxiesList[i]也是list类型，分别存入队列
        checkDataQueue.put(proxy)
    proxiesList = []
    # 创建一个线程锁，防止多线程写入文件时发生错乱
    mutex_lock = threading.Lock()
    # 线程数为500，在一定范围内，线程数越多，速度越快。
    # 小心点，别变成ddos把验证服务器干死
    for i in range(500):
        t = threading.Thread(target=checkProxy, name='LoopThread' + str(i))
        t.start()
