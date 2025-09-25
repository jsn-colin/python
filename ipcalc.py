from ip import IPV4
import sys

def ipv4_aggregator(start_ip, end_ip):
    '''对多个ip地址进行CIDR聚合'''
    sip = IPV4(start_ip)
    eip = IPV4(end_ip)

    # 包含多少个ip, 这个数字一定是大于1的数据，否则起始ip大于结束ip
    ip_num = eip.ip_int - sip.ip_int + 1
    if ip_num < 1:
        raise ValueError("起始 IP 不能大于结束 IP")
    cur_ip = start_ip
    ip_ret = list()
    while True:
        # mask = 32 - ip_num.bit_length() + 1 # 这种方法可行，但是codon不支持，另外如果使用codon build ipcalc.py，开头的from ip import IPV4,需要改成直接把IPV4类拷贝到文件的开头
        mask = 35 - len(bin(ip_num)) 
        for cmask in range(mask, 33, 1):
            cip = IPV4(cur_ip + '/' + str(cmask))
            if cip.ip_network == cur_ip:
                ip_ret.append(cur_ip + '/' + str(cmask))
                broadcast_int = int(cip.ip_bin_broadcast, 2)
                next_ip   = '.'.join(str((broadcast_int + 1 >> i) & 0xFF) for i in (24, 16, 8, 0))
                cur_ip = next_ip
                ip_num = ip_num - cip.ip_count
                found = True # 只要for循环中找到一个就是true
                if ip_num <= 0:
                    return ip_ret
                break
        if not found:
            raise RuntimeError(f"无法为 {cur_ip} 找到合适的子网掩码")
        
def usage():
    pass
    print(f"\t执行:\t{sys.argv[0]} \t\t手动输入网段，打印 ip所在网段信息")
    print(f"\t执行:\t{sys.argv[0]} -f file \t -f 指定文件，打印 ip所在网段信息")
    print(f"\t执行:\t{sys.argv[0]} -bf file \t -bf 根据 '网络位,广播位' 聚合成网段")
    print("\t\t\t\t文件格式：'192.168.1.0,192.168.1.9' 每行一条")

def main():
    if len(sys.argv) == 1:
        while True:
            ip_str = input('请输入网段(ip/mask)[Q/q]: 退出： ').strip()
            if ip_str.lower() in ('q', 'quit', 'exit'):
                sys.exit(0)
            else:
                ip = IPV4(ip_str)
                print(f'ip地址是：{ip.ip}')
                print(f'ip掩码是：{ip.mask}')
                print(f'ip网络是：{ip.ip_network}')
                print(f'ip广播是：{ip.ip_broadcast}')
                print(f'二进制网络：{ip.ip_bin_network}')
                print(f'二进制广播：{ip.ip_bin_broadcast}')
                print(f'ip十进制是：{ip.ip_int}')
                print(f'网段拥有的ip地址数是：{ip.ip_count}')

    elif sys.argv[1] == '-f':
        try:
            with open(sys.argv[2], 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ip = IPV4(line)
                        if ip:
                            print(f'ip地址是：{ip.ip}')
                            print(f'ip掩码是：{ip.mask}')
                            print(f'ip网络是：{ip.ip_network}')
                            print(f'ip广播是：{ip.ip_broadcast}')
                            print(f'二进制网络：{ip.ip_bin_network}')
                            print(f'二进制广播：{ip.ip_bin_broadcast}')
                            print(f'ip十进制是：{ip.ip_int}')
                            print(f'网段拥有的ip地址数是：{ip.ip_count}')
        except FileNotFoundError:
            print(f"错误：文件 {sys.argv[2]} 不存在")
            sys.exit(1)

    elif sys.argv[1] == '-bf':
        try:
            with open(sys.argv[2], 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        start_ip, end_ip = line.split(',')
                        ip_list = ipv4_aggregator(start_ip, end_ip)
                        print(f'{start_ip}-{end_ip} 聚合列表:-> {ip_list}')

        except Exception as e:
            print(f"处理 -bf 时出错: {e}")
    else:
        usage()

if __name__ =="__main__":
    main()
