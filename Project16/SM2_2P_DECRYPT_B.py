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
from threading import Thread

HOST = ''
PORT = 50007


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



def SIGN_2P_B(d2, conn, addr):
    while True:
        # 接收T1
        t1_0 = conn.recv(1024).decode()
        conn.sendall("I have get T1[0]".encode())
        t1_1 = conn.recv(1024).decode()
        conn.sendall("I have get T1[1]".encode())
        t1_0 = int(t1_0)
        t1_1 = int(t1_1)
        T1 = (t1_0, t1_1)



        #计算T2
        T2 = Mul_Add(T1[0], T1[1], gmpy2.invert(d2, n))

        # 给A发送T2
        conn.sendall(str(T2[0]).encode())
        data_1 = conn.recv(1024).decode()
        print("A发来的消息: ", data_1, '\n')
        conn.sendall(str(T2[1]).encode())
        data_2 = conn.recv(1024).decode()
        print("A发来的消息: ", data_2, '\n')

        break
    conn.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(10)
print('Listening on port:', PORT)
conn, addr = sock.accept()
print('Connected by', addr)
d2 = conn.recv(1024).decode()
d2 = int(d2)
mthread = Thread(target = SIGN_2P_B, args = (d2, conn, addr))
mthread.start()
sock.close()