#!/bin/env python3
# _*_coding:utf-8_*_


# Author = "colin"
# First Time: 2020/04/17
# Version:1.0

# 2020/07/27
# Version:2.0
# 新增 -f 参数指定ip地址文件

# 2020/09/10
# Version:3.0
# 新增 -bf 利用"网络位,广播位"，汇总成网段，只针对标准地址段

# 2020/09/12
# Version：3.1
# 新增 -abf 参数， a = all 使 -bf 可以对任意非标准的地址聚合成多个地址段
# -bf 针对 “网络位,广播位”，只能聚合成一个标准网段  -abf 针对“起始IP,结束IP” 聚合成多个标准的地址段

# 2025/04/13
# Version：3.2
# 优化代码，统一风格，支持codon编译及运行


import re
import sys


VERSION = 3.2


def check_ip(ip):
    """检查ip是否合法"""
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False


def ip2cov10(binip):
    # 32位数字切割
    binip1 = binip[0:8]
    binip2 = binip[8:16]
    binip3 = binip[16:24]
    binip4 = binip[24:]

    # 将二进制转为10进制
    decip1 = str(int(binip1, 2))
    decip2 = str(int(binip2, 2))
    decip3 = str(int(binip3, 2))
    decip4 = str(int(binip4, 2))
    decip = decip1 + '.' + decip2 + '.' + decip3 + '.' + decip4

    return decip


def net2ip(ip, mask):
    """将网段转换为IP地址"""
    p1, p2, p3, p4 = ip.split('.')

    # 将ip四段转化为二进制
    #pb1 = '{:08b}'.format(int(p1))
    pb1 = f"{int(p1):b}"
    pb2 = f"{int(p2):b}"
    pb3 = f"{int(p3):b}"
    pb4 = f"{int(p4):b}"
    pb = pb1 + pb2 + pb3 + pb4

    # 网络位
    netbit = pb[0:int(mask)]

    # 主机位该补充的0和1
    umask = int(32 - int(mask))
    sup0 = '0' * umask
    sup1 = '1' * umask

    # 网络地址 = 网络位 + 补充0的个数 ；广播地址 = 网络位 + 补充的1的个数
    net_bit_comp = netbit + sup0  # 网络地址
    host_bit_comp = netbit + sup1  # 广播地址

    # 将二进制的网络地址和广播地址转化为ip格式
    net_dec = ip2cov10(net_bit_comp)
    host_dec = ip2cov10(host_bit_comp)

    print(f"{net_dec} --- {host_dec}")
    print(f"二进制网络地址： {net_bit_comp}")
    print(f"二进制广播地址： {host_bit_comp}")


def net2ip2(ip, mask):
    """将网段转换为IP地址"""
    if ip is not None:
        p1, p2, p3, p4 = ip.split('.')

        # 将ip四段转化为二进制
        pb1 = f"{int(p1):b}"
        pb2 = f"{int(p2):b}"
        pb3 = f"{int(p3):b}"
        pb4 = f"{int(p4):b}"
        pb = pb1 + pb2 + pb3 + pb4

        # 网络位，主机位
        netbit = pb[0:int(mask)]

        # 主机位该补充的0和1
        umask = int(32 - int(mask))
        sup0 = '0' * umask
        sup1 = '1' * umask

        # 网络地址 = 网络位 + 补充0的个数 ；广播地址 = 网络位 + 补充的1的个数
        net_bit_comp = netbit + sup0  # 网络地址
        host_bit_comp = netbit + sup1  # 广播地址

        # 将二进制的网络地址和广播地址转化为ip格式
        net_dec = ip2cov10(net_bit_comp)
        host_dec = ip2cov10(host_bit_comp)

        return net_dec, host_dec
    else:
        sys.exit(1)


def ipcovnum(ip_addr):
    check_result = check_ip(ip_addr)

    if check_result:

        p1, p2, p3, p4 = ip_addr.split(".")
        p1 = int(p1) * (256 ** 3)
        p2 = int(p2) * (256 ** 2)
        p3 = int(p3) * 256
        p4 = int(p4)

        pnum = p1 + p2 + p3 + p4
        return pnum

    else:
        print(f"{ip_addr} is error")


def numcovip(num_addr):
    if num_addr >= 16777217:
        nip1 = num_addr // (256 ** 3)
        nip = num_addr % (256 ** 3)
        nip2 = nip // (256 ** 2)
        nip = nip % (256 ** 2)
        nip3 = nip // 256
        nip = nip % 256
        nip = nip % 256

        ip = str(nip1) + '.' + str(nip2) + '.' + str(nip3) + '.' + str(nip)
        return ip

    else:
        print(f"{num_addr} is error")


def excute_proc(ipstart, ipstop):
    for mask in range(1, 33):
        ip1, ip2 = net2ip2(ipstart, mask)
        if ip1 == ipstart:
            if ipcovnum(ip2) <= ipcovnum(ipstop):

                ret = (ipstart, mask)
                # print(result)
                return ret

            elif ipcovnum(ip2) == ipcovnum(ipstop):
                break


def inter_proc(ipbegin, ipend):
    results = list()
    while True:
        iplist = excute_proc(ipbegin, ipend)
        if iplist is not None:
            ip1, ip2 = net2ip2(iplist[0], iplist[1])
            ipbegin = numcovip(ipcovnum(ip2) + 1)
            results.append(iplist)

        else:
            break
    return results


def main():
    """手工执行 计算网段中的 网络位和广播位"""
    net = input('请输入网段（ip/mask）[Q/q]:退出： ')
    if net == 'q' or net == 'quit' or net == 'Q':
        sys.exit(1)
    else:
        try:
            ip, mask = net.split('/')
            if check_ip(ip):  # 判断ip是否合法

                if 32 >= int(mask) >= 1:  # 判断掩码是否合法
                    net2ip(ip, mask)

                else:
                    print('子网掩码地址不合规')
            else:
                print('ip地址不合规')
        except:
            print("输入格式为：ip/mask，例如：192.168.10.10/24")


def main2(net):
    """指定文件 计算网段的 网络为和广播位"""
    ip, mask = net.split("/")
    if check_ip(ip):  # 判断ip是否合法
        if 32 >= int(mask) >= 1:  # 判断掩码是否合法
            netpool = net2ip2(ip, mask)
            return net[:-1] + " --> " + netpool[0] + "--" + netpool[1]
        else:
            return net[:-1] + " --> " + "子网掩码不合规"
    else:
        return net[:-1] + " --> " + "ip地址不合规"


def main3(ip_start, ip_end):
    """指定文件 对提供网络位和广播位 的地址进行地址汇总"""
    if check_ip(ip_start):
        if check_ip(ip_end):
            ip2 = ipcovnum(ip_end)
            ip1 = ipcovnum(ip_start)

            ret = ip2 - ip1 + 1

            for num in range(32):
                if ret == 2 ** num:
                    mask = 32 - num
                    return f"{ip_start}/{mask}"

        else:
            return ip_end + "-->" + "地址不合法"
    else:
        return ip_start + "-->" + "地址不合法"


def main3_1(ip_range):
    """
    执行该函数，传入‘192.168.1.1，192.168.1.9’格式参数
    返回[('192.168.1.1', 32), ('192.168.1.2', 31), ('192.168.1.4', 30), ('192.168.1.8', 31)]
    """

    ipstart, ipstop = ip_range.split(',')
    # 判断 起始IP地址合法性
    if check_ip(ipstart):
        # 判断 结束ip合法性
        if check_ip(ipstop):
            # 计算 进程会返回 一个ip段的列表
            ret = inter_proc(ipstart, ipstop)
            return ret
        else:
            # 结束ip 不合法
            print("{ipstop} is error")
    else:
        # 起始ip 不合法
        print("{ipstart} is error")


def Usage():

    print("Vnersio: {VERSION}")
    print()
    print("Example:")

    print("\t执行:\t" + sys.argv[0] + "\t\t（手动输入网段，打印出: '网络位 -- 广播位'）")
    print("\t执行:\t" + sys.argv[0] + ' -f file ' + "\t（-f 指定文件， 打印出: '网络位 -- 广播位'）")
    print("\t执行:\t" + sys.argv[0] + ' -bf file ' + "\t（-b 反向，根据'网络位,广播位'   聚合成网段）")
    print("\t\t\t\t -bf 文件格式：'192.168.1.0,192.168.1.255'一行一条记录\n")
    print("\t执行:\t" + sys.argv[0] + ' -abf file ' + "\t（-a all ; -b 反向，根据'起始IP,结束IP'   聚合成网段）")
    print("\t\t\t\t -abf 文件格式：'192.168.1.0,1.168.1.9'一行一条记录")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        while True:
            main()  # 手工查询

    elif sys.argv[1] == '-f':
        for line in open(sys.argv[2]):
            result = main2(line)  # 文件查询
            print(result)

    elif sys.argv[1] == '-bf':
        for line in open(sys.argv[2]):
            ips, ipe = line.split(',')
            result = main3(ips, ipe)
            # print(result)
            if result:
                print(f"{ips},{ipe}.strip('\n') -- {result}")
            else:
                print(f"{ips},{ipe}.strip('\n') -- None")

    elif sys.argv[1] == '-abf':
        for lines in open(sys.argv[2]):
            result = main3_1(lines)
            # ret 是一个聚合后的列表文件，但由于格式缘故，需要以下的代码对返回的格式进行优化
            ret1 = list()
            for i in result:
                j = i[0] + "/" + str(i[1])

                ret1.append(j)
            # ret1 是转换过格式的ret
            print(f"{lines}.strip('\n') -- {ret1}")

    else:
        Usage()
