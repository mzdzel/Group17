# pylint: disable=missing-module-docstring
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
import binascii
import base64
import random
from cryptography.fernet import Fernet

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
def encrypt(m, public_key):
    plen = len(hex(p)[2:])
    m1 = m.encode().hex()
    m1 = int(m1, 16)
    m = '0' * ((4 - (len(Int_bin(m1)) % 4)) % 4) + Int_bin(m1)
    klen = len(m)
    #k = generate_k(m.encode(), private_key)
    k = 0x123456956248634323a56474873e2f1
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
    return (c1, c2, c3)


# 解密函数
def decrypt(c1, c2, c3, private_key):
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



# 密钥协商
# 密钥协商
def key_change(sa, sb, pa, pb, ida,idb):
    ida = ida.encode().hex()
    ENTLa = '{:04X}'.format(len(ida) * 4)
    za = ENTLa + ida + '{:064X}'.format(a)+'{:064X}'.format(b)+'{:064X}'.format(Gx)+'{:064X}'.format(Gy)+'{:064X}'.format(pa[0])+'{:064X}'.format(pa[1])
    za = hex(int(sm3(za),16))[2:]
    idb = idb.encode().hex()
    ENTLb = '{:04X}'.format(len(idb) * 4)
    zb = ENTLb + idb + '{:064X}'.format(a)+'{:064X}'.format(b)+'{:064X}'.format(Gx)+'{:064X}'.format(Gy)+'{:064X}'.format(pb[0])+'{:064X}'.format(pb[1])
    zb = hex(int(sm3(zb),16))[2:]
    w = math.ceil(math.ceil(math.log2(n))/2) - 1
    while True:
        ra = random.randint(1, n)
        Ra = Mul_Add(Gx, Gy, ra)
        # 判断Ra是否满足椭圆曲线方程
        if pow(Ra[1], 2, p) == (pow(Ra[0], 3, p) + a * Ra[0] + b) % p:
            break
    x1 = pow(2, w) + (Ra[0] & (pow(2, w) - 1))
    ta = (sa + x1 * ra) % n
    while True:
        rb = random.randint(1, n)
        Rb = Mul_Add(Gx, Gy, rb)
        # 判断Ra是否满足椭圆曲线方程
        if pow(Rb[1], 2, p) == (pow(Rb[0], 3, p) + a * Rb[0] + b) % p:
            break
    x2 = pow(2,w) + (Rb[0] & (pow(2, w) - 1))
    tb = (sb + x2 * rb) % n
    #密钥长度为256bit
    klen = 256 

    temp1 = Mul_Add(Ra[0], Ra[1], x1)
    A1 = Add(pa[0], pa[1], temp1[0], temp1[1])
    V = Mul_Add(A1[0], A1[1], tb)
    if (len(hex(p)[2:]) * 4 == 192):
        vx, vy = '{:0192b}'.format(V[0]), '{:0192b}'.format(V[1])
    else:
        vx, vy = '{:0256b}'.format(V[0]), '{:0256b}'.format(V[1])
    kb = KDF(hex(int(vx, 2))[2:] + hex(int(vy, 2))[2:] + za + zb, klen)
    l = str(0x02)
    ll = str(0x03)
    SB = sm3(l + vy + sm3(vx + za + zb + hex(Ra[0])[2:] + hex(Ra[1])[2:] + hex(Rb[0])[2:] + hex(Rb[1])[2:]))

    temp2 = Mul_Add(Rb[0], Rb[1], x2)
    B1 = Add(pb[0], pb[1], temp2[0], temp2[1])
    U = Mul_Add(B1[0], B1[1], ta)
    if (len(hex(p)[2:]) * 4 == 192):
        ux, uy = '{:0192b}'.format(U[0]), '{:0192b}'.format(U[1])
    else:
        ux, uy = '{:0256b}'.format(U[0]), '{:0256b}'.format(U[1])
    S1 = sm3(l + uy + sm3(ux + za + zb + hex(Ra[0])[2:] + hex(Ra[1])[2:] + hex(Rb[0])[2:] + hex(Rb[1])[2:]))
    if S1 != SB:
        return False
    ka = KDF(hex(int(ux, 2))[2:] + hex(int(uy, 2))[2:] + za + zb, klen)
    SA = sm3(ll + uy + sm3(ux + za + zb + hex(Ra[0])[2:] + hex(Ra[1])[2:] + hex(Rb[0])[2:] + hex(Rb[1])[2:]))
    S2 = sm3(ll + vy + sm3(vx + za + zb + hex(Ra[0])[2:] + hex(Ra[1])[2:] + hex(Rb[0])[2:] + hex(Rb[1])[2:]))
    if S2 != SA:
        return False
    ka = hex(int(ka, 2))[2:]
    ka = binascii.a2b_hex(ka).decode()
    return ka


# 加密
def PGP_SM2_ENCRYPT(M, PUBLIC_KEY, KEY):
    # 加密对称密钥
    Chip_KEY = encrypt(KEY, PUBLIC_KEY)
    # 创建加密器
    KEY = KEY.encode()
    KEY = base64.b64encode(KEY)
    cipher = Fernet(KEY)
    # 加密数据
    encrypted_data = cipher.encrypt(M.encode())
    return Chip_KEY, encrypted_data.decode()




# 解密
def PGP_SM2_DECRYPT(C1, C2, C3, CHIP_TEXT, PRIVATE_KEY):
    # 解密对称密钥
    KEY_DECRYPT = decrypt(C1, C2, C3, PRIVATE_KEY)
    # 创建加密器
    KEY_DECRYPT = KEY_DECRYPT.encode()
    KEY_DECRYPT = base64.b64encode(KEY_DECRYPT)
    cipher = Fernet(KEY_DECRYPT)
    # 解密数据
    decrypted_data = cipher.decrypt(CHIP_TEXT.encode())
    return decrypted_data.decode()


# 示例

# 明文
data = "THANKS"

# 密钥协商
idA = "banana"
idB = "apple"
Private_A = 0x2359076592ACDF6423673737215635672EE127FD34386956
Public_A = Mul_Add(Gx, Gy, Private_A)
Private_B = 0xA359076592ACDFD4236737372E5639672EE111FD34A36942
Public_B = Mul_Add(Gx, Gy, Private_B)
K = key_change(Private_A, Private_B, Public_A, Public_B, idA, idB)

# 获取公私钥
private_k = 0x2359076592ACDF6423673737215635672EE127FD34386956
public_k = Mul_Add(Gx, Gy, private_k)
Chiperkey, Chiper = PGP_SM2_ENCRYPT(data, public_k, K)
Message = PGP_SM2_DECRYPT(Chiperkey[0], Chiperkey[1], Chiperkey[2], Chiper, private_k)
print("明文是: ", data, "\n")
print("密文是: ", Chiper, "\n")
print("协商的密钥是: ", K, '\n')
print("加密后的密钥是: ", Chiperkey[0], Chiperkey[1], Chiperkey[2], "\n")
print("解密后的数据是: ", Message, "\n")

# 测试效率
s1 = time.time()
for i in range(1,1000):
    Chiperkey, Chiper = PGP_SM2_ENCRYPT(data, public_k, K)
    Message = PGP_SM2_DECRYPT(Chiperkey[0], Chiperkey[1], Chiperkey[2], Chiper, private_k)
s2 = time.time()
print("测量1000次运行时间为: ", s2 - s1)
print("测量1次运行时间为: ", (s2 - s1) / 1000)
