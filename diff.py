#!/usr/bin/env python3
# _*_coding:utf-8_*_

import sys
import chardet


def get_list(file):
    glist = list()
    f = open(file, 'rb')  # 先用二进制打开
    data = f.read()  # 读取文件内容
    file_encoding = chardet.detect(data).get('encoding')  # 得到文件的编码格式
    with open(file, 'r', encoding=file_encoding)as f1:  # 使用得到的文件编码格式打开文件
        lines = f1.readlines()
        for line in lines:
            glist.append(line.strip())
    return glist


def main():
    list1 = get_list(sys.argv[1])
    list2 = get_list(sys.argv[2])
    on1 = set(list1).difference(set(list2))  # 只在list1中的
    on2 = set(list2).difference(set(list1))  # 只在list2中的
    public = set(list1).intersection(set(list2))  # 交集

    print('只在%s中的： [%d]' % (sys.argv[1], len(on1)))
    print('-------------->')
    for i in on1:
        print(i)
    print('<--------------')
    print('只在%s中的： [%d]' % (sys.argv[2], len(on2)))
    print('-------------->')
    for i in on2:
        print(i)
    print('<--------------')
    print('public： [%d]' % len(set(public)))
    print('-------------->')
    for i in public:
        print(i)
    print('-------------->')

if __name__ == '__main__':
    main()
