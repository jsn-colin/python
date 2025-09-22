#!/bin/env python3
# _*_coding:utf-8_*_

# Author = "colin"
# First Time: 2020/04/17
# Version: 1.0
# 2020/07/27 - Version 2.0: 新增 -f 参数指定 ip 地址文件
# 2020/09/10 - Version 3.0: 新增 -bf 利用"网络位,广播位"，汇总成网段（仅标准网段）
# 2020/09/12 - Version 3.1: 新增 -abf，支持任意起始/结束 IP 聚合为多个标准网段
# 2025/04/13 - Version 3.2: 优化代码风格，支持 codon 编译及运行

import re
import sys

VERSION = 3.2


def check_ip(ip):
    """检查 IP 是否合法"""
    p = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    return bool(p.match(ip.strip()))  # 同时去除空格和换行


def ip2cov10(binip):
    """将 32 位二进制字符串转换为点分十进制 IP"""
    if len(binip) != 32:
        raise ValueError(f"二进制字符串长度必须为 32，当前为 {len(binip)}")
    binip1 = binip[0:8]
    binip2 = binip[8:16]
    binip3 = binip[16:24]
    binip4 = binip[24:32]

    decip1 = str(int(binip1, 2))
    decip2 = str(int(binip2, 2))
    decip3 = str(int(binip3, 2))
    decip4 = str(int(binip4, 2))
    return decip1 + '.' + decip2 + '.' + decip3 + '.' + decip4


def net2ip(ip, mask):
    """将网段转换为网络位和广播位，并打印"""
    try:
        p1, p2, p3, p4 = ip.split('.')
        # 转为 8 位二进制（关键修复：补零）
        pb1 = f"{int(p1):08b}"
        pb2 = f"{int(p2):08b}"
        pb3 = f"{int(p3):08b}"
        pb4 = f"{int(p4):08b}"
        pb = pb1 + pb2 + pb3 + pb4

        if len(pb) != 32:
            print(f"错误：二进制长度不是 32 位（当前 {len(pb)}）")
            return

        netbit = pb[0:int(mask)]  # 网络位
        umask = 32 - int(mask)    # 主机位数
        sup0 = '0' * umask        # 主机位补 0（网络地址）
        sup1 = '1' * umask        # 主机位补 1（广播地址）

        net_bit_comp = netbit + sup0  # 网络地址二进制
        host_bit_comp = netbit + sup1 # 广播地址二进制

        net_dec = ip2cov10(net_bit_comp)
        host_dec = ip2cov10(host_bit_comp)

        print(f"{net_dec} --- {host_dec}")
        print(f"二进制网络地址： {net_bit_comp}")
        print(f"二进制广播地址： {host_bit_comp}")

    except Exception as e:
        print(f"处理 {ip}/{mask} 时出错: {e}")


def net2ip2(ip, mask):
    """将网段转换为网络位和广播位，返回元组 (网络地址, 广播地址)"""
    if ip is None:
        return None, None
    try:
        p1, p2, p3, p4 = ip.split('.')
        pb1 = f"{int(p1):08b}"
        pb2 = f"{int(p2):08b}"
        pb3 = f"{int(p3):08b}"
        pb4 = f"{int(p4):08b}"
        pb = pb1 + pb2 + pb3 + pb4

        netbit = pb[0:int(mask)]
        umask = 32 - int(mask)
        sup0 = '0' * umask
        sup1 = '1' * umask

        net_bit_comp = netbit + sup0
        host_bit_comp = netbit + sup1

        net_dec = ip2cov10(net_bit_comp)
        host_dec = ip2cov10(host_bit_comp)

        return net_dec, host_dec
    except:
        return None, None


def ipcovnum(ip_addr):
    """IP 地址转为整数"""
    ip_addr = ip_addr.strip()
    if not check_ip(ip_addr):
        print(f"{ip_addr} is error")
        return None
    p1, p2, p3, p4 = map(int, ip_addr.split("."))
    return p1 * (256**3) + p2 * (256**2) + p3 * 256 + p4


def numcovip(num_addr):
    """整数转为 IP 地址"""
    if not (0 <= num_addr <= 0xFFFFFFFF):
        print(f"{num_addr} is out of range")
        return None
    nip1 = num_addr // (256**3)
    num_addr %= (256**3)
    nip2 = num_addr // (256**2)
    num_addr %= (256**2)
    nip3 = num_addr // 256
    nip4 = num_addr % 256
    return f"{nip1}.{nip2}.{nip3}.{nip4}"


def excute_proc(ipstart, ipstop):
    """尝试找到能覆盖 [ipstart, ipstop] 的最短网段"""
    start_num = ipcovnum(ipstart)
    stop_num = ipcovnum(ipstop)
    if start_num is None or stop_num is None:
        return None

    for mask in range(32, 0, -1):  # 从大网段（小掩码）开始尝试
        net_start, net_end = net2ip2(ipstart, mask)
        if net_start is None:
            continue
        net_start_num = ipcovnum(net_start)
        net_end_num = ipcovnum(net_end)
        if net_start_num <= start_num and net_end_num >= stop_num:
            return (net_start, mask)
    return None


def inter_proc(ipbegin, ipend):
    """将 IP 范围聚合为多个最优网段"""
    results = []
    begin_num = ipcovnum(ipbegin)
    end_num = ipcovnum(ipend)
    if begin_num is None or end_num is None:
        return results

    current = begin_num
    while current <= end_num:
        current_ip = numcovip(current)
        # 从 /32 开始尝试最大网段
        for mask in range(32, 0, -1):
            net_start, net_end = net2ip2(current_ip, mask)
            if net_start is None:
                continue
            net_end_num = ipcovnum(net_end)
            if net_end_num <= end_num:
                results.append((current_ip, mask))
                current = net_end_num + 1
                break
    return results


def main():
    """手动输入网段，显示网络位和广播位"""
    while True:
        net = input('请输入网段（ip/mask）[Q/q]: 退出： ').strip()
        if net.lower() in ('q', 'quit'):
            sys.exit(0)
        try:
            ip, mask = net.split('/')
            if check_ip(ip):
                if 1 <= int(mask) <= 32:
                    net2ip(ip, mask)
                else:
                    print('子网掩码不合规（1-32）')
            else:
                print('IP 地址不合规')
        except Exception as e:
            print("输入格式为：ip/mask，例如：192.168.10.10/24")


def main2(net):
    """处理文件中的网段，返回字符串结果"""
    net = net.strip()
    if not net or net.startswith('#'):
        return ""
    try:
        ip, mask = net.split("/")
        if check_ip(ip) and 1 <= int(mask) <= 32:
            net_start, net_end = net2ip2(ip, mask)
            return f"{net} --> {net_start} -- {net_end}"
        else:
            return f"{net} --> IP 或掩码不合规"
    except:
        return f"{net} --> 格式错误"


def main3(ip_start, ip_end):
    """根据网络位和广播位反推网段（仅标准网段）"""
    ip_start, ip_end = ip_start.strip(), ip_end.strip()
    if not check_ip(ip_start) or not check_ip(ip_end):
        return f"{ip_start},{ip_end} --> 地址不合法"

    start_num = ipcovnum(ip_start)
    end_num = ipcovnum(ip_end)
    if start_num is None or end_num is None:
        return f"{ip_start},{ip_end} --> 转换失败"

    total = end_num - start_num + 1
    for num in range(33):
        if total == (1 << num):  # 2 ** num
            mask = 32 - num
            return f"{ip_start}/{mask}"
    return f"{ip_start},{ip_end} --> 无法聚合成单个标准网段"


def main3_1(ip_range):
    """将任意 IP 范围聚合成多个标准网段"""
    ip_range = ip_range.strip()
    try:
        ipstart, ipstop = ip_range.split(',')
        if check_ip(ipstart) and check_ip(ipstop):
            result = inter_proc(ipstart, ipstop)
            return [(item[0], item[1]) for item in result]
        else:
            print(f"{ip_range} --> IP 地址不合法")
            return []
    except Exception as e:
        print(f"解析失败: {e}")
        return []


def Usage():
    print(f"Version: {VERSION}")
    print("Example:")
    print(f"\t执行:\t{sys.argv[0]} \t\t（手动输入网段，打印 '网络位 -- 广播位'）")
    print(f"\t执行:\t{sys.argv[0]} -f file \t（-f 指定文件，打印 '网络位 -- 广播位'）")
    print(f"\t执行:\t{sys.argv[0]} -bf file \t（-bf 根据 '网络位,广播位' 聚合成网段）")
    print("\t\t\t\t文件格式：'192.168.1.0,192.168.1.255' 每行一条")
    print(f"\t执行:\t{sys.argv[0]} -abf file \t（-abf 根据 '起始IP,结束IP' 聚合成多个网段）")
    print("\t\t\t\t文件格式：'192.168.1.0,192.168.1.9' 每行一条")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1] == '-f':
        try:
            with open(sys.argv[2], 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        result = main2(line)
                        if result:
                            print(result)
        except FileNotFoundError:
            print(f"错误：文件 {sys.argv[2]} 不存在")
            sys.exit(1)
    elif sys.argv[1] == '-bf':
        try:
            with open(sys.argv[2], 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ips, ipe = line.split(',', 1)
                        result = main3(ips, ipe)
                        print(result)
        except Exception as e:
            print(f"处理 -bf 时出错: {e}")
    elif sys.argv[1] == '-abf':
        try:
            with open(sys.argv[2], 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        result = main3_1(line)
                        ret1 = [f"{ip}/{mask}" for ip, mask in result]
                        print(f"{line} --> {ret1}")
        except Exception as e:
            print(f"处理 -abf 时出错: {e}")
    else:
        Usage()
