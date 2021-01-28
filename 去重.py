# -*- codeing = utf-8 -*-
# @Time : 2021/1/27 14:40
# @Author : 96bearli
# @File : 去重.py
# @Software : PyCharm

import shutil

readPath = 'proxy1.txt'
writePath = 'proxy.txt'
lines_seen = set()
outfiile = open(writePath, 'a+', encoding='utf-8')
f = open(readPath, 'r', encoding='utf-8')
for line in f:
    if line not in lines_seen:
        outfiile.write(line)
        lines_seen.add(line)
