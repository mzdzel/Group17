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
# pylint: disable=W0611
# pylint: disable=W0622
# pylint: disable=W0612
# pylint: disable=R0914
# pylint: disable=R1705
import time
import gmpy2
import random
import socket
import sys


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

HOST = '127.0.0.1'
PORT = 50007
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    SOCKET.connect((HOST, PORT))
except Exception as e:
    print('Server not found or not open')
    sys.exit()


# 签名算法
def SIGN_2P_A(Message):
    # First Step
    d1 = random.randint(1, n - 1)
    p1 = Mul_Add(Gx, Gy, gmpy2.invert(d1, n))

    


    
    # 发送P1
    SOCKET.sendall(str(p1[0]).encode())
    data1 = SOCKET.recv(1024).decode()
    print("B发来的消息: ", data1, '\n')
    SOCKET.sendall(str(p1[1]).encode())
    data2 = SOCKET.recv(1024).decode()
    print("B发来的消息: ", data2, '\n')

     # Third Step
    Z = "I can do whatever I want to do"
    M = Z + Message
    e = sm3(M)
    k1 = random.randint(1, n - 1)
    Q1 = Mul_Add(Gx, Gy, k1)

    # 将e和Q1发给B
    SOCKET.sendall(e.encode())
    data3 = SOCKET.recv(1024).decode()
    print("B发来的消息: ", data3, '\n')
    SOCKET.sendall(str(Q1[0]).encode())
    data4 = SOCKET.recv(1024).decode()
    print("B发来的消息: ", data4, '\n')
    SOCKET.sendall(str(Q1[1]).encode())
    data5 = SOCKET.recv(1024).decode()
    print("B发来的消息: ", data5, '\n')

    # 接收B发来的r, s2, s3
    r = SOCKET.recv(1024).decode()
    SOCKET.sendall("I get r ".encode())
    s2 = SOCKET.recv(1024).decode()
    SOCKET.sendall("I get s2 ".encode())
    s3 = SOCKET.recv(1024).decode()

    r = int(r)
    s2 = int(s2)
    s3 = int(s3)
 
    # Fifth Step
    s = ((d1 * k1) * s2 + d1 * s3 - r) % n
    if s == 0 and s == n - r:
        print("\n签名失败!\n")
        return False
    SOCKET.close()
    return hex(r)[2:], hex(s)[2:]

# 示例
MESSAGE = "I am Homelander"
time_start = time.time()
SIGNATURE_R, SIGNATURE_S = SIGN_2P_A(MESSAGE)
time_end = time.time()
print("消息：", MESSAGE, "\n")
print("r: ", SIGNATURE_R, "\n")
print("S: ", SIGNATURE_S, "\n")
print("耗时: ", time_end - time_start, '\n')