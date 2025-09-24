import re

class IPV4:
    def __init__(self, ip_str: str):
        parts = ip_str.strip().split('/')
        if len(parts) > 2:
            raise ValueError("IP地址格式错误，应为 'ip' 或 'ip/mask'")
        
        if not self.check_ipv4(parts[0]):
            raise ValueError(f"无效的IP地址: {parts[0]}")
        self.ip = parts[0]
        
        if len(parts) == 1:
            self.mask = None
        else:
            try:
                mask_value = int(parts[1])
                if 1 <= mask_value <= 32:
                    self.mask = mask_value
                else:
                    raise ValueError(f"子网掩码必须在 1-32 之间，得到的是 {mask_value}")
            except ValueError:
                raise ValueError(f"子网掩码必须是整数，得到的是 '{parts[1]}'")

    def check_ipv4(self, ip_str):
        p = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        return p.match(ip_str) is not None

    @property
    def ip_int(self):
        parts = self.ip.split('.')
        return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

    @property
    def ip_bin(self):
        return ''.join(bin(int(x))[2:].zfill(8) for x in self.ip.split('.'))

    @property
    def ip_bin_network(self):
        if self.mask is not None and self.mask != 32:
            return self.ip_bin[:self.mask] + '0' * (32 - self.mask)
        else:
            return self.ip_bin  # 直接复用

    @property
    def ip_bin_broadcast(self):
        if self.mask is not None and self.mask != 32:
            return self.ip_bin[:self.mask] + '1' * (32 - self.mask)
        else:
            return self.ip_bin  # 直接复用

    def _bin_to_ip(self, bin_str):
        """将32位二进制字符串转为点分十进制IP"""
        return '.'.join(str(int(bin_str[i:i+8], 2)) for i in range(0, 32, 8))

    @property
    def ip_network(self):
        return self._bin_to_ip(self.ip_bin_network)

    @property
    def ip_broadcast(self):
        return self._bin_to_ip(self.ip_bin_broadcast)


# 使用
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("用法: python ip.py <ip/mask>")
        sys.exit(1)
    
    ip = IPV4(sys.argv[1])
    print(f'ip地址是：{ip.ip}')
    print(f'ip掩码是：{ip.mask}')
    print(f'ip网络是：{ip.ip_network}')
    print(f'ip广播是：{ip.ip_broadcast}')
    print(f'二进制网络：{ip.ip_bin_network}')
    print(f'二进制广播：{ip.ip_bin_broadcast}')
    print(f'ip十进制是：{ip.ip_int}')
