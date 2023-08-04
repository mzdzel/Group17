import gmpy2
import math
import random
from gmssl import sm3

#secp256k1中的参数标准
p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
k = 0xACE1224817DC81273B123878A98DF49623AAAA564651AEFA

 # 整数转二进制
def Int_bin(N):
    res = []
    while N != 0:
        res.append(str(N & 1))
        N = N >> 1
    res.reverse()
    return "".join(res)

#国密sm3加密
def sm3_hash(message):
    message = message.encode()
    msg_list = [i for i in message]
    hash_hex = sm3.sm3_hash(msg_list)
    return hash_hex

# 定义点加
def Add(x1, y1, x2, y2):
    if x1 == x2 and y1 == p - y2:
        return False
    if x1 != x2:
        l = ((y2 - y1) * gmpy2.invert(x2 - x1, p)) % p
    else:
        l = (((3 * x1 * x1 + a) % p) * gmpy2.invert(2 * y1, p)) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return x3, y3

# 定义点乘
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
    for i in range(math.ceil(klen / 256)):
        temp = (xy + '{:032b}'.format(count)).encode().hex()
        t = t + sm3_hash(temp).encode().hex()
        count += 1
    x = int(t, 16)
    x = Int_bin(x)
    t = '0' * ((256 - (len(x) % 256)) % 256) + x
    return t[:klen]

# 签名函数
def sign(m, ID, private_key):
    public_key = Mul_Add(Gx, Gy, private_key)
    ID = ID.encode().hex()
    ENTL = '{:04X}'.format(len(ID) * 4)
   Za = ENTL + ID + '{:064X}'.format(a) + '{:064X}'.format(b) + '{:064X}'.format(Gx) + '{:064X}'.format(
        Gy) + '{:064X}'.format(public_key[0]) + '{:064X}'.format(public_key[1])
    hash_m = hex(int(sm3_hash(Za), 16))[2:]
    m = hash_m + m
    e = sm3_hash(m)
    x1, y1 = Mul_Add(Gx, Gy, k)
    r = (int(e, 16) + x1) % n
    s = (gmpy2.invert(1 + private_key, n) * (k - r * private_key)) % n
    r = hex(r)[2:]
    s = hex(s)[2:]
    return r, s

def ALICE_BOB(R, S):
    R = int(R, 16)
    S = int(S, 16)
    D = k - S
    D = D * gmpy2.invert(S + R, n) % n
   # D = D % n
    return D

# Alice的消息
M_1 = "abc"

# Bob的消息
M_2 = "xyz"

# Alice的ID
ALICE_ID = "ALICE"

# BOb的ID
BOB_ID = "BOB"

# Alice的私钥
d_alice = random.randint(1, n)

# Bob的私钥
d_bob = random.randint(1, n)

r_alice, s_alice = sign(M_1, ALICE_ID, d_alice)
r_bob, s_bob = sign(M_2, BOB_ID, d_bob)

# Alice计算Bob的私钥
d2 = ALICE_BOB(r_bob, s_bob)

# Bob计算Alice的私钥
d1 = ALICE_BOB(r_alice, s_alice)

print("----------------------------------- Alice与Bob的私钥 -------------------------------------------------------")
print("Alice的私钥：", d_alice)
print("BOB的私钥: ", d_bob)
print("----------------------------------- Alice与Bob的签名 -------------------------------------------------------")
print("Alice的签名： r: ", r_alice, " s: ", s_alice)
print("BOb的签名： r: ", r_bob, " s: ", s_bob)
print("----------------------------------- 计算得到二者的私钥 -------------------------------------------------------")
print("Alice计算的Bob的私钥: ", d2)
print("BOb计算的Alice的私钥: ", d1)

