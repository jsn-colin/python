# _*_coding:utf-8 _*_

import random, base64, json
from itertools import cycle


class StrCryption:
    """
    该类用于对字符串进行加解密使用, 实例化类时需要传递一个密钥key（任意字符串）
    """

    def __init__(self, key):
        self.key = key
        self.bs64key = base64.b64encode(self.key.encode('utf-8')).decode('utf-8')

        self.keyord = list()
        for i in self.bs64key:
            self.keyord.append(ord(i))

        # 构造一个默认使用的字符串映射字典
        self.CODEMAP = {
        '0x0': 'RD', '0x1': 'at', '0x2': 'UY', '0x3': 'PY', '0x4': 'lV', '0x5': 'Yl', '0x6': 'WL', 
        '0x7': 'wy', '0x8': 'Uj', '0x9': 'kG', '0xa': 'hO', '0xb': 'oZ', '0xc': 'nU', '0xd': 'Pf', 
        '0xe': 'PD', '0xf': 'MM', '0x10': 'dt', '0x11': 'ZK', '0x12': 'll', '0x13': 'PT', '0x14': 'uf',
        '0x15': 'oa', '0x16': 'xn', '0x17': 'zl', '0x18': 'AA', '0x19': 'rI', '0x1a': 'zE', '0x1b': 'Qv',
        '0x1c': 'Lv', '0x1d': 'Zs', '0x1e': 'of', '0x1f': 'Ag', '0x20': 'LN', '0x21': 'Tq', '0x22': 'Vk', 
        '0x23': 'En', '0x24': 'EQ', '0x25': 'PM', '0x26': 'SN', '0x27': 'kV', '0x28': 'HK', '0x29': 'iA', 
        '0x2a': 'ob', '0x2b': 'Eg', '0x2c': 'kX', '0x2d': 'OM', '0x2e': 'aY', '0x2f': 'Qa', '0x30': 'Ot', 
        '0x31': 'UB', '0x32': 'Od', '0x33': 'cj', '0x34': 'zT', '0x35': 'wH', '0x36': 'tC', '0x37': 'dX', 
        '0x38': 'Fs', '0x39': 'pI', '0x3a': 'Tt', '0x3b': 'pS', '0x3c': 'rl', '0x3d': 'iC', '0x3e': 'hJ', 
        '0x3f': 'Zv', '0x40': 'in', '0x41': 'IS', '0x42': 'IP', '0x43': 'fO', '0x44': 'yC', '0x45': 'Yd', 
        '0x46': 'ci', '0x47': 'aE', '0x48': 'Ei', '0x49': 'Ue', '0x4a': 'nY', '0x4b': 'mY', '0x4c': 'ld', 
        '0x4d': 'CN', '0x4e': 'Im', '0x4f': 'TI', '0x50': 'mc', '0x51': 'NB', '0x52': 'gJ', '0x53': 'jF', 
        '0x54': 'eM', '0x55': 'zY', '0x56': 'nL', '0x57': 'au', '0x58': 'YN', '0x59': 'pR', '0x5a': 'HY', 
        '0x5b': 'OW', '0x5c': 'Wp', '0x5d': 'ql', '0x5e': 'YF', '0x5f': 'Lw', '0x60': 'zi', '0x61': 'kK', 
        '0x62': 'bK', '0x63': 'mo', '0x64': 'sd', '0x65': 'OL', '0x66': 'yD', '0x67': 'Pu', '0x68': 'Pt', 
        '0x69': 'ii', '0x6a': 'qv', '0x6b': 'uZ', '0x6c': 'XI', '0x6d': 'bX', '0x6e': 'lW', '0x6f': 'Zf', 
        '0x70': 'Qp', '0x71': 'qP', '0x72': 'ge', '0x73': 'Aq', '0x74': 'so', '0x75': 'Dj', '0x76': 'bw', 
        '0x77': 'NS', '0x78': 'ao', '0x79': 'li', '0x7a': 'yt', '0x7b': 'Fq', '0x7c': 'Av', '0x7d': 'Sr', 
        '0x7e': 'ZB', '0x7f': 'dJ'
        }
        self.CODEMAP.update(dict(zip(self.CODEMAP.values(), self.CODEMAP.keys())))  # 生成反向映射

    def add_codemap(self, codemap):
        self.CODEMAP = json.loads(codemap)
        if len(self.CODEMAP) == 128:
            self.CODEMAP.update(dict(zip(self.CODEMAP.values(), self.CODEMAP.keys())))  # 生成反向映射
        else:
            raise "CODEMAP error"

    def encode(self, content):
        """加密的字符串需要是utf-8编码，解密同样"""
        content = str(content)
        bs64str = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        #print('base64后的字符', bs64str)

        keyord = cycle(self.keyord)

        strord = list()
        for i in bs64str:
            strord.append(ord(i))
        #print("strord:", strord)
        # 加密后的数字列表
        cryord = list()
        for i, j in zip(strord, keyord):
            cryord.append(i ^ j)
        #print("cryord:", cryord)
        # 加密的数字列表映射的字符串
        crycode = str()
        for i in cryord:
            crycode = crycode + self.CODEMAP.get(hex(i))
        #print("crycode:", crycode)
        return crycode

    def decode(self, crycode):
        # key的数字
        keyord = cycle(self.keyord)

        # 加密后的字典值
        cryord = list()
        while True:
            cryord.append(self.CODEMAP.get(crycode[0:2]))
            crycode = crycode[2:]
            if not crycode:
                break

        # 解密后转成的列表的数字
        conord = list()
        for i, j in zip(cryord, keyord):
            conord.append(int(i, 16) ^ j)

        # 解密后的ascii
        constr = str()
        for i in conord:
            constr = constr + chr(i)

        # 对bs64的ascii解码
        content = base64.b64decode(constr).decode('utf-8')
        return content


class BinCryption:
    """该类用于对字二进制文件进行加解密使用, 实例化类时需要传递一个密钥key（任意字符串）
    """

    def __init__(self, key):
        self.key = key
        self.bs64key = base64.b64encode(self.key.encode('utf-8')).decode('utf-8')

        self.keyord = list()
        for i in self.bs64key:
            self.keyord.append(ord(i))

        # 构造一个默认使用的字符串映射字典
        self.CODEMAP =         self.CODEMAP = {
        '0x0': 'RD', '0x1': 'at', '0x2': 'UY', '0x3': 'PY', '0x4': 'lV', '0x5': 'Yl', '0x6': 'WL', 
        '0x7': 'wy', '0x8': 'Uj', '0x9': 'kG', '0xa': 'hO', '0xb': 'oZ', '0xc': 'nU', '0xd': 'Pf', 
        '0xe': 'PD', '0xf': 'MM', '0x10': 'dt', '0x11': 'ZK', '0x12': 'll', '0x13': 'PT', '0x14': 'uf',
        '0x15': 'oa', '0x16': 'xn', '0x17': 'zl', '0x18': 'AA', '0x19': 'rI', '0x1a': 'zE', '0x1b': 'Qv',
        '0x1c': 'Lv', '0x1d': 'Zs', '0x1e': 'of', '0x1f': 'Ag', '0x20': 'LN', '0x21': 'Tq', '0x22': 'Vk', 
        '0x23': 'En', '0x24': 'EQ', '0x25': 'PM', '0x26': 'SN', '0x27': 'kV', '0x28': 'HK', '0x29': 'iA', 
        '0x2a': 'ob', '0x2b': 'Eg', '0x2c': 'kX', '0x2d': 'OM', '0x2e': 'aY', '0x2f': 'Qa', '0x30': 'Ot', 
        '0x31': 'UB', '0x32': 'Od', '0x33': 'cj', '0x34': 'zT', '0x35': 'wH', '0x36': 'tC', '0x37': 'dX', 
        '0x38': 'Fs', '0x39': 'pI', '0x3a': 'Tt', '0x3b': 'pS', '0x3c': 'rl', '0x3d': 'iC', '0x3e': 'hJ', 
        '0x3f': 'Zv', '0x40': 'in', '0x41': 'IS', '0x42': 'IP', '0x43': 'fO', '0x44': 'yC', '0x45': 'Yd', 
        '0x46': 'ci', '0x47': 'aE', '0x48': 'Ei', '0x49': 'Ue', '0x4a': 'nY', '0x4b': 'mY', '0x4c': 'ld', 
        '0x4d': 'CN', '0x4e': 'Im', '0x4f': 'TI', '0x50': 'mc', '0x51': 'NB', '0x52': 'gJ', '0x53': 'jF', 
        '0x54': 'eM', '0x55': 'zY', '0x56': 'nL', '0x57': 'au', '0x58': 'YN', '0x59': 'pR', '0x5a': 'HY', 
        '0x5b': 'OW', '0x5c': 'Wp', '0x5d': 'ql', '0x5e': 'YF', '0x5f': 'Lw', '0x60': 'zi', '0x61': 'kK', 
        '0x62': 'bK', '0x63': 'mo', '0x64': 'sd', '0x65': 'OL', '0x66': 'yD', '0x67': 'Pu', '0x68': 'Pt', 
        '0x69': 'ii', '0x6a': 'qv', '0x6b': 'uZ', '0x6c': 'XI', '0x6d': 'bX', '0x6e': 'lW', '0x6f': 'Zf', 
        '0x70': 'Qp', '0x71': 'qP', '0x72': 'ge', '0x73': 'Aq', '0x74': 'so', '0x75': 'Dj', '0x76': 'bw', 
        '0x77': 'NS', '0x78': 'ao', '0x79': 'li', '0x7a': 'yt', '0x7b': 'Fq', '0x7c': 'Av', '0x7d': 'Sr', 
        '0x7e': 'ZB', '0x7f': 'dJ'
        }
        self.CODEMAP.update(dict(zip(self.CODEMAP.values(), self.CODEMAP.keys())))

    def add_codemap(self, codemap):
        self.CODEMAP = json.loads(codemap)
        if len(self.CODEMAP) == 128:
            self.CODEMAP.update(dict(zip(self.CODEMAP.values(), self.CODEMAP.keys())))  # 生成反向映射
        else:
            raise "CODEMAP error"

    def encode(self, content):
        """加密的字符串需要是utf-8编码，解密同样"""
        #bs64str = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        bs64str = base64.b64encode(content)
        keyord = cycle(self.keyord)

        strord = list()
        for i in bs64str:
            strord.append(i)

        # 加密后的数字列表
        cryord = list()
        for i, j in zip(strord, keyord):
            cryord.append(i ^ j)

        # 加密的数字列表映射的字符串
        crycode = str()
        for i in cryord:
            crycode = crycode + self.CODEMAP.get(hex(i))

        return crycode

    def decode(self, crycode):
        # key的数字
        keyord = cycle(self.keyord)

        # 加密后的字典值
        cryord = list()
        while True:
            cryord.append(self.CODEMAP[crycode[0:2]])
            crycode = crycode[2:]
            if not crycode:
                break

        # 解密后转成的列表的数字
        conord = list()
        for i, j in zip(cryord, keyord):
            conord.append(int(i, 16) ^ j)

        # 解密后的ascii
        constr = str()
        for i in conord:
            constr = constr + chr(i)

        # 对bs64的ascii解码
        #content = base64.b64decode(constr).decode('utf-8')
        content = base64.b64decode(constr)

        return content


class CreateCodeMap:
    """
       用于生成一个映射字典 cdbk = CreateCodeMap.create_codemap()
       配合StrCryption.add_codemap(cdbk)，使用，将映射字典放入字符串加密的类中
    """

    @staticmethod
    def _create_codemap():
        string_map = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/+$%'
        while True:
            codemap = dict()
            for i in range(0, 128):
                txt1 = random.choice(string_map)
                txt2 = random.choice(string_map)
                txt = txt1 + txt2
                codemap[hex(i)] = txt
 
            return codemap

    @staticmethod
    def create_codemap():
        while True:
            codemap = CreateCodeMap._create_codemap()
            # 判断字典中没有重合的键值
            if len(codemap) == 128:
                break
            
        return json.dumps(codemap)


if __name__ == '__main__':
    print('version: 1.1 \ndate: 2021-03-04 \nauthor: colin \nEmail: 740391452@qq.com')
