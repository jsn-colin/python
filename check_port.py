#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2021/9/4 2:00
# @Author   : colin
# @Email    : 740391452@qq.com
# @File     : checkport.py
# @Software : PyCharm


import re
import sys
import os
import signal
import socket
import chardet
import argparse
from multiprocessing import Pool

VERSION = '1.0.0-py3'
RED = '\033[31m'
GREEN = '\033[32m'
END = '\033[0m'

parser = argparse.ArgumentParser(description='checkport version:%s' % VERSION)
# parser.add_argument('-h', '--help', action="store_true", default=False, help='显示本页信息后退出')
parser.add_argument('-v', '--version', action="store_true", default=False, help='版本信息')
parser.add_argument('-s', '--server', dest='server', help='指定目的地址 (可以是单个地址，可以是地址段，格式 "192.168.1.0/24")')
parser.add_argument('-f', '--file', dest='file', help='指定文件路径 (一行一条记录，格式 "192.168.1.1:80")')
parser.add_argument('-p', '--port', dest='port', type=int, help='指定端口 1-65535')
parser.add_argument('-t', '--timeout', dest='timeout', default=3, type=int, help='指定超时时间，默认：3s')
parser.add_argument('-P', '--process', dest='process_pool', default=os.cpu_count(), type=int, help='进程池数量，默认：单进程')
parser.add_argument('-W', '--width', dest='width', default=35, type=int, help='对齐宽度，默认：35')
args = parser.parse_args()


def getlist_fromfile(file):
    """执行该函数，传入文件名，得到一个去重，去空字符串的列表"""
    f = open(file, 'rb')
    data = f.read()
    f.close()
    file_encoding = chardet.detect(data).get('encoding')
    with open(file, 'r', encoding=file_encoding) as f1:
        lines = f1.readlines()  # lines 是一个列表
        line_list = list()
        for i in lines:
            tmp = re.sub(r'\s+', '', i)  # 去除空白字符
            tmp = tmp.split('#')[0]  # 去除'#'号后面的，没有'#',无所谓
            if len(tmp) != 0:
                line_list.append(tmp)
        return line_list


def getip_fromnet(net):
    """传入：192.168.1.10/24类型,返回一个IP地址列表"""
    ip_list = list()
    ip, mask = net.split('/')
    if ip is not None:
        ip1, ip2, ip3, ip4 = ip.split('.')
        hosts_num = 2 ** (32 - int(mask))  # 网段的主机总数
        # 将ip四段转化为十进制数字
        ipnum = (int(ip1) * (256 ** 3)) + (int(ip2) * (256 ** 2)) + (int(ip3) * 256) + int(ip4)
        # 得到网络位和广播位十进制数字
        hosts_net = ipnum - (ipnum % hosts_num)
        hosts_board = (ipnum - (ipnum % hosts_num) + hosts_num)
        # 得到网络为十进制数字（取模）
        ipnum_tmp = hosts_net
        for i in range(hosts_num):
            if hosts_board >= ipnum_tmp >= hosts_net:
                iptmp = str(ipnum_tmp // (256 ** 3)) + '.' + str((ipnum_tmp % (256 ** 3)) // (256 ** 2)) + '.' + str((ipnum_tmp % (256 ** 2)) // (256)) + '.' + str(ipnum_tmp % (256))
                ip_list.append(iptmp)
                ipnum_tmp = ipnum_tmp + 1

        return ip_list
    else:
        exit(1)


def check_port(ip, port):
    """ 执行函数传入ip和port """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(args.timeout)
    if ip and port:
        try:
            s.connect((ip, int(port)))
            s.shutdown(2)
            print(((ip + ':' + str(port)).ljust(args.width)) + ('[%sDone%s]' % (GREEN, END)))
            return True
        except:
            print(((ip + ':' + str(port)).ljust(args.width)) + ('[%sFail%s]' % (RED, END)))
            return False
    else:
        print('ip或端口不存在: %s' % (ip + ':' + str(port)))
        return 1


def check_server(server, port):
    if port:
        ip = server.split(':')[0]
        if '/' in ip:
            ip_list = getip_fromnet(ip)
            print('待检测主机数: %d' % len(ip_list))
            for i in ip_list:
                po.apply_async(check_port, (i, port))  # 将任务加入进程池
        else:
            check_port(ip, port)
    else:
        try:
            ip, port = server.split(':')
            if '/' in ip:
                ip_list = getip_fromnet(ip)
                print('待检测主机数: %d' % len(ip_list))
                for i in ip_list:
                    po.apply_async(check_port, (i, port))  # 将任务加入进程池
            else:
                po.apply_async(check_port, (ip, port))  # 将任务加入进程池
        except:
            print('ip或端口不存在')
            exit(100)


def check_file(lines, port):
    ip_list = list()
    if port:
        # 通过-p 指定了port
        for line in lines:
            ip = line.split(':')[0]
            if '/' in line:
                tmp = getip_fromnet(ip)
                ip_list.extend(tmp)
            else:
                ip_list.append(ip)
        # 去重
        ip_list = list(set(ip_list))
        print('待检测主机数: %d' % len(ip_list))
        for i in ip_list:
            po.apply_async(check_port, (i, port))  # 将任务加入进程池

    else:
        # 没有-p指定端口，需要从文件中读取端口
        for line in lines:
            line = line.strip()  # 去掉每行后面的换行符
            try:
                net, port = line.split(':')
            except:
                print((line.ljust(args.width)) + ('[%s端口不存在%s]' % (RED, END)))
                continue
            else:
                if '/' in net:
                    ip_list_tmp = getip_fromnet(net)
                    for i in ip_list_tmp:
                        if {i: port} in ip_list:  # 判读是否重复填加（去重）
                            continue
                        else:
                            ip_list.append({i: port})
                else:
                    if {net: port} in ip_list:  # 判读是否重复填加（去重）
                        continue
                    else:
                        ip_list.append({net: port})

        # 获这里列表没有去重，ip_list是一个列表套字典的值
        print('待检测主机数: %d' % len(ip_list))
        for i in ip_list:  # i 实际上是一个字典,键名是ip，键值是port
            for key in i:
                po.apply_async(check_port, (key, i[key]))  # 将任务加入进程池


def quit(signum, frame):
    print('%s%s%s' % (RED, '终止执行', END))
    sys.exit(1)


def main():
    if args.version:
        print(VERSION)
        exit(0)
    if args.server:
        if args.port:
            check_server(args.server, args.port)
        else:
            port = False
            check_server(args.server, port)
    if args.file:
        lines = getlist_fromfile(args.file)  # 得到一个文件行列表
        if args.port:
            check_file(lines, args.port)
        else:
            port = False
            check_file(lines, port)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    po = Pool(args.process_pool)  # 创建进程池，进程池属于全局变量
    main()  # 添加进程在mian函数里调用
    po.close()  # 关闭进程池的添加
    po.join()  # 主进程进入堵塞状态，等待进程池完成
