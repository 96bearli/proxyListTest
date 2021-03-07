# 说明

* 从github拉取proxylist，**本地验活**后保存为txt文档
* 使用**多线程**加快速度 
* **type可选**
* **自动去重**
* 原始地址访问失败后尝试**自动更换镜像**地址
* 验证方法：~~requests.get(url="http://icanhazip.com/", proxies=Proxy)~~
* 验证方法：采用双重验证**telnet+req**获取高质量代理

# 添加源

## 注意

对于文档的要求: 

1. 一行一条，可以有无效行
2. 需要utf-8编码才能使通用提取函数生效（大概）

## 模板
添加于代码中函数定义前
```python
# 获取代理信息的格式模板
# 文档url+模式+匹配ip规则+匹配端口规则+匹配模式规则
# 当type不固定时对应"mix"
# 默认使用的telnet方法，有需求可以自行修改checkProxy()

# raw2_http
# 62.171.170.82:3128
raw = {"url": 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
        "type": "http",
        "findIp": re.compile(r'(\d+?\.\d+?\.\d+?\.\d+?):'),
        "findPort": re.compile(r':(\d+?)\n'),
        "findType": ""}
raws.append(raw)
```

# 免责

本项目因为兴趣而生，开源仅供测试。