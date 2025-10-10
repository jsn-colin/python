import re

class IPV4:
    def __init__(self, ip_str: str):
        parts = ip_str.strip().split('/')
        if len(parts) > 2:
            raise ValueError("IP地址格式错误，应为 'ip' 或 'ip/mask'")
        
        if self.check_ipv4(parts[0]) is None:
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
        if p.match(ip_str):
            return ip_str  # 匹配成功，返回 IP 字符串
        else:
            return None    # 匹配失败，返回 None
    
    # ip相关属性
    @property
    def ip_dec(self):
        return self._ip_to_decimal(self.ip)
        
    @property
    def ip_bin(self):
        return self._ip_to_bin(self.ip)

    # 网络码相关属性
    @property
    def network(self):
        return self._bin_to_ip(self.network_bin)

    @property
    def network_dec(self):
        return self._ip_to_decimal(self.network)

    @property
    def network_bin(self):
        if self.mask is not None and self.mask != 32:
            return self.ip_bin[:self.mask] + '0' * (32 - self.mask)
        else:
            return self.ip_bin  # 直接复用
        
    # 广播相关属性
    @property
    def broadcast(self):
        return self._bin_to_ip(self.broadcast_bin)

    @property
    def broadcast_dec(self):
        return self._ip_to_decimal(self.broadcast)
    
    @property
    def broadcast_bin(self):
        if self.mask is not None and self.mask != 32:
            return self.ip_bin[:self.mask] + '1' * (32 - self.mask)
        else:
            return self.ip_bin  # 直接复用
    
    # 其他属性
    @property
    def count(self):
        return int(self.broadcast_bin, 2) - int(self.network_bin, 2) + 1

    def get_next(self, ip_str = None):
        if ip_str is None:
            return self._bin_to_ip(bin(self.ip_dec + 1)[2:])
        else:
            if self.check_ipv4(ip_str) is None:
                raise ValueError(f"无效的IP地址: {ip_str}")
            else:
                return self._decimal_to_ip(self._ip_to_decimal(ip_str) + 1)

    def get_previous(self, ip_str = None):
        if ip_str is None:
            return self._bin_to_ip(bin(self.ip_dec - 1)[2:])
        else:
            if self.check_ipv4(ip_str) is None:
                raise ValueError(f"无效的IP地址: {ip_str}")
            else:
                return self._decimal_to_ip(self._ip_to_decimal(ip_str) - 1)

   # ip处理方法
    def _ip_to_decimal(self, ip_str):
        """将字符串ip转为十进制数字"""
        parts = ip_str.split('.')
        return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

    def _ip_to_bin(self, ip_str):
        """将字符串ip转为二进制"""
        return ''.join(bin(int(x))[2:].zfill(8) for x in ip_str.split('.'))

    def _bin_to_ip(self, ip_bin):
        """将32位二进制字符串转为字符串IP"""
        return '.'.join(str(int(ip_bin[i:i+8], 2)) for i in range(0, 32, 8))

    def _decimal_to_ip(self, ip_dec):
        """将十进制数字转为字符串IP"""
        return '.'.join(str((ip_dec >> i) & 0xFF) for i in (24, 16, 8, 0))

# 使用
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("用法: python ip.py <ip/mask>")
        sys.exit(1)
    
    ip = IPV4(sys.argv[1])
    print(f'ip地址是：{ip.ip}')
    print(f'ip掩码是：{ip.mask}')
    print(f'ip网络是：{ip.network}')
    print(f'ip广播是：{ip.broadcast}')
    print(f'二进制网络：{ip.network_bin}')
    print(f'二进制广播：{ip.broadcast_bin}')
    print(f'ip十进制是：{ip.ip_dec}')
    print(f'网段拥有的ip地址数是：{ip.count}')
