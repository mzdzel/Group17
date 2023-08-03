# pylint: disable=import-error
# pylint: disable=C0103
# pylint: disable=C0411
# pylint: disable=C0114
# pylint: disable=C0116
# pylint: disable=C0103
# pylint: disable=C0209
# pylint: disable=C0301
# pylint: disable=C0303
# pylint: disable=C0304
# pylint: disable=C0325
# pylint: disable=W0621
# pylint: disable=W0622
# pylint: disable=W0612
# pylint: disable=R0914
# pylint: disable=R1705

import gmpy2
import math
import time
import hashlib
import hmac
import binascii

def Int_bin(N):
    # 整数转二进制
    res = []
    while N != 0:
        res.append(str(N & 1))
        N = N >> 1
    res.reverse()
    return "".join(res)

def sm3(s: str) -> str:

    # 初始值
    IV = 0x7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e
    MAX_32 = 0xffffffff

    # 32位循环左移
    def left_shift(x: int, i: int) -> int:
        return ((x << (i % 32)) & MAX_32) + (x >> (32 - i % 32))

    # 常量T
    def T(j: int) -> int:
        if 0 <= j <= 15:
            return 0x79cc4519
        return 0x7a879d8a

    # 布尔函数
    def FF(j: int, x: int, y: int, z: int) -> int:
        if 0 <= j <= 15:
            return x ^ y ^ z
        return (x & y) | (x & z) | (y & z)

    # 布尔函数
    def GG(j: int, x: int, y: int, z: int) -> int:
        if 0 <= j <= 15:
            return x ^ y ^ z
        return (x & y) | (~x & z)

    # 置换函数
    def P0(x: int) -> int:
        return x ^ left_shift(x, 9) ^ left_shift(x, 17)

    # 置换函数
    def P1(x: int) -> int:
        return x ^ left_shift(x, 15) ^ left_shift(x, 23)

    # 消息填充函数，对长度为l(l < 2^64)比特的消息s，填充至长度为512比特的倍数
    def fill(s: str) -> str:
        v = 0
        for i in s:
            v <<= 8
            v += ord(i)
        msg = Int_bin(v).zfill(len(s) * 8)
        k = (960 - len(msg) - 1) % 512
        return hex(int(msg + '1' + '0' * k + Int_bin(len(msg)).zfill(64), 2))[2:]

    m = fill(s)

    # 迭代过程
    for i in range(len(m) // 128):

        # 消息扩展
        Bi = m[i * 128: (i + 1) * 128]
        W = []
        for j in range(16):
            W.append(int(Bi[j * 8: (j + 1) * 8], 16))

        for j in range(16, 68):
            W.append(P1(W[j - 16] ^ W[j - 9] ^ left_shift(W[j - 3], 15)) ^ left_shift(W[j - 13], 7) ^ W[j - 6])
        W1 = []
        for j in range(64):
            W1.append(W[j] ^ W[j + 4])

        A, B, C, D, E, F, G, H = [IV >> ((7 - i) * 32) & MAX_32 for i in range(8)]

        # 迭代计算
        for j in range(64):
            ss1 = left_shift((left_shift(A, 12) + E + left_shift(T(j), j)) & MAX_32, 7)
            ss2 = ss1 ^ left_shift(A, 12)
            tt1 = (FF(j, A, B, C) + D + ss2 + W1[j]) & MAX_32
            tt2 = (GG(j, E, F, G) + H + ss1 + W[j]) & MAX_32
            D = C
            C = left_shift(B, 9)
            B = A
            A = tt1
            H = G
            G = left_shift(F, 19)
            F = E
            E = P0(tt2)
        IV ^= ((A << 224) + (B << 192) + (C << 160) + (D << 128) + (E << 96) + (F << 64) + (G << 32) + H)
    return hex(IV)[2:].zfill(64)  


# 定义SM2椭圆曲线参数
p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0

# 椭圆曲线点加
def Add(x1, y1, x2, y2):
    if x1 == x2 and y1 == p-y2:
        return False
    if x1 != x2:
        l = ((y2 - y1) * gmpy2.invert(x2 - x1, p)) % p
    else:
        l = (((3 * x1 * x1 + a) % p) * gmpy2.invert(2 * y1, p)) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return x3, y3


# 椭圆曲线点乘
def Mul_Add(x, y, n):                   
    n = Int_bin(n)
    qx, qy = x, y
    for i in range(1, len(n)):
        qx, qy = Add(qx, qy, qx, qy)
        if n[i] == '1':
            qx, qy = Add(qx, qy, x, y)
    return (qx, qy)


# 获取公私钥
private_key = 0x2359076592ACDF6423673737215635672EE127FD34386956
public_key = Mul_Add(Gx, Gy, private_key)


# 生成 K

q = int(str(p), 16)
qlen = 256
data1 = ''.join([chr(item) for item in range(256)])
  
def Bits2int(S):
    # 二进制字符串转int
    blen = len(S)
    if qlen < blen:
        S = S[:qlen]
    else:
        S = (qlen - blen) * "0" + S
    int_data = 0
    blen = len(S)
    while blen > 0:
        int_data *= 2
        int_data += data1.find(S[0])
        S = S[1:]
        blen = len(S)
    return int_data


def int2octets(S):
    oct_data = ""
    while S > 0:
        temp = S % 256
        oct_data += data1[temp]
        S = S // 256
    rlen = len(oct_data)
    if rlen >= 32:
        return oct_data
    oct_data += 'a' * (32 - rlen)
    return oct_data


def bits2octets(S):
    # 二进制字符串转8bit一组的字符串
    A = Bits2int(S) % q
    B = int2octets(A)
    return B


def generate_k(m):
    h1 = sm3(m.decode())
    v = '\x01' * 32
    k = '\x00' * 32
    k = hmac.new(k.encode(), (v + '\x00' + int2octets(private_key) + bits2octets(h1)).encode(), hashlib.sha256).digest()
    v = hmac.new(k, v.encode(), hashlib.sha256).digest()
    k = hmac.new(k, v + ('\x01' + int2octets(private_key) + bits2octets(h1)).encode(), hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    tlen = 0
    T = b''
    while tlen < qlen:
        v = hmac.new(k, v, hashlib.sha256).digest()
        T = T + v
        tlen = len(T)
    T = T.decode(errors='ignore')
    K = Bits2int(T)
    if K >= 1 & K < q:
        return K
    else:
        while K >= q:
            k = hmac.new(k, v + ('\x00').encode(), hashlib.sha256).digest()
            v = hmac.new(k, v, hashlib.sha256).digest()
            K = Bits2int(T.decode(errors='ignore'))
    return K

# 明文
data = "123456"


def KDF(xy, klen):
    t = ''
    count = 1
    for i in range(math.ceil(klen/256)):
        temp = (xy + '{:032b}'.format(count)).encode().hex()
        t = t + sm3(temp).encode().hex()
        count += 1
    x = int(t, 16)
    x = Int_bin(x)
    t = '0' * ((256-(len(x) % 256)) % 256) + x
    return t[:klen]


# 加密函数
def encrypt(m):
    plen = len(hex(p)[2:])
    m1 = m.encode().hex()
    m1 = int(m1, 16)
    m = '0' * ((4 - (len(Int_bin(m1)) % 4)) % 4) + Int_bin(m1)
    klen = len(m)
    k = generate_k(m.encode())
    x2, y2 = Mul_Add(public_key[0], public_key[1], k)
    if(len(hex(p)[2:]) * 4 == 192):
        x2, y2 = '{:0192b}'.format(x2), '{:0192b}'.format(y2)
    else:
        x2, y2 = '{:0256b}'.format(x2), '{:0256b}'.format(y2)
    t = KDF(x2 + y2, klen)
    x1, y1 = Mul_Add(Gx, Gy, k)
    x1, y1 = (plen - len(hex(x1)[2:])) * '0' + hex(x1)[2:], (plen - len(hex(y1)[2:])) * '0' + hex(y1)[2:]
    c1 = x1 + y1
    temp = int(m,2) ^ int(t, 2)
    temp = hex(temp)[2:]
    Tlen = len(temp)
    c2 = ((klen//4) - Tlen) * '0' + temp
    c3 = sm3(hex(int(x2 + m + y2, 2))[2:])
    return c1, c2, c3


# 解密函数
def decrypt(c1, c2, c3):
    x1, y1 = int(c1[:len(c1) // 2], 16), int(c1[len(c1) // 2:], 16)
    x2, y2 = Mul_Add(x1, y1, private_key)
    if (len(hex(p)[2:]) * 4 == 192):
        x2, y2 = '{:0192b}'.format(x2), '{:0192b}'.format(y2)
    else:
        x2, y2 = '{:0256b}'.format(x2), '{:0256b}'.format(y2)
    klen = len(c2) * 4
    t = KDF(x2 + y2, klen)
    if int(t, 2) == 0:
        return False
    temp = int(c2, 16) ^ int(t, 2)
    temp = Int_bin(temp)
    Tlen = len(temp)
    m = '0' * (klen - Tlen) + temp
    u = sm3(hex(int(x2 + m + y2, 2))[2:])
    if u != c3:
        return False
    message_dec = hex(int(m, 2))[2:]
    message_dec = binascii.a2b_hex(message_dec).decode()
    return message_dec

# 签名函数
def sign(m, ID):
    k = generate_k(m.encode())
    ID = ID.encode().hex()
    ENTL='{:04X}'.format(len(ID) * 4)
    m1=ENTL + ID + '{:064X}'.format(a)+'{:064X}'.format(b)+'{:064X}'.format(Gx)+'{:064X}'.format(Gy)+'{:064X}'.format(public_key[0])+'{:064X}'.format(public_key[1])
    hash_m = hex(int(sm3(m1),16))[2:]
    m = hash_m + m 
    e = sm3(m)
    x1,y1 = Mul_Add(Gx, Gy, k)
    r = (int(e, 16) + x1) % n
    s = (gmpy2.invert(1 + private_key, n) * (k - r * private_key)) % n
    r = hex(r)[2:]
    s = hex(s)[2:]
    return r, s




# 验证函数
def verify(r,s,ID,m):
    ID = ID.encode().hex()
    ENTL = '{:04X}'.format(len(ID) * 4)
    m1 = ENTL + ID + '{:064X}'.format(a)+'{:064X}'.format(b)+'{:064X}'.format(Gx)+'{:064X}'.format(Gy)+'{:064X}'.format(public_key[0])+'{:064X}'.format(public_key[1])
    hash_m = hex(int(sm3(m1),16))[2:]
    if int(r, 16) not in range(1, n-1):
        return False
    if int(s, 16) not in range(1, n-1):
        return False
    m = hash_m + m
    e = sm3(m)
    t=(int(r, 16) + int(s, 16)) % n
    if t == 0:
        return False
    x1, y1 = Mul_Add(public_key[0], public_key[1], t)
    x2, y2 = Mul_Add(Gx, Gy, int(s, 16))
    x1, y1 = Add(x1, y1, x2, y2)
    R=(int(e, 16) + x1) % n
    if(hex(R)[2:] == r):
        return True
    return False



# 加解密函数示例
C1, C2, C3 = encrypt(data)
print("明文: ", data, "\n")
print("c1: ", C1, "\n")
print("c2: ", C2, "\n")
print("c3: ", C3, "\n")
message = decrypt(C1, C2, C3)
print("解密结果为: ", message, "\n")

# 加解密函数测量效率
s1 = time.time()
for i in range(1,1000):
    c1,c2,c3=encrypt(data)
    m2=decrypt(c1,c2,c3)
s2 = time.time()
print("测量1000次运行时间为: ", s2 - s1, "\n")
print("测量1次运行时间为: ", (s2 - s1) / 1000, "\n")


# 签名及验证函数示例
id = "Banana"
signature_r, signature_s = sign(data, id)
verify_result = verify(signature_r, signature_s, id, data)
print("消息：", data, "\n")
print("签名r: ",signature_r, "\n")
print("签名s: ",signature_s, "\n")
print("验证结果:",verify_result, "\n")

# 签名及验证函数测量效率
s3 = time.time()
for i in range(1,1000):
    signature = sign(data, id)
    verify_result = verify(signature[0], signature[1], id, data)
s4 = time.time()
print("测量1000次运行时间为: ", s4 - s3, "\n")
print("测量1次运行时间为: ", (s4 - s3) / 1000, "\n")