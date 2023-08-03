import gmpy2
import sympy

# 二次剩余
def QR(a, p):
    k = 0
    P = (p - 1)
    if p % 4 == 3:
        return gmpy2.powmod(a, int((p + 1) // 4), p)
    else:
        while P % 2 == 0:
            P = P // 2
            k = k + 1
        q = 2
        while q:
            l = gmpy2.powmod(q, int((p - 1) // 2), p)
            if l == p - 1:
                break
            q = sympy.nextprime(q)
        b = gmpy2.powmod(q, P, p)
        x = [0 for i in range(k)]
        re_a = gmpy2.invert(a, p)
        x[k - 1] = gmpy2.powmod(a, int((P + 1) // 2), p)
        for i in range(1, k):
            m = re_a * pow(x[k - i], 2)
            n = pow(2, (k - i - 1))
            if gmpy2.powmod(m, n, p) == p - 1:
                j0 = 1
                x[k - i - 1] = x[k - i] * pow(b, j0 * (2 ** (i - 1))) % p
            else:
                j1 = 0
                x[k - i - 1] = x[k - i] % p
        return x[0]
    

def Int_bin(N):
    # 整数转二进制
    res = []
    while N != 0:
        res.append(str(N & 1))
        N = N >> 1
    res.reverse()
    return "".join(res)

# sm3
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
    if x1 == y1 == 0:
        return [x2, y2]
    if x1 == x2 and y1 == p-y2:
        return False
    if x1 != x2:
        l = ((y2 - y1) * gmpy2.invert(x2 - x1, p)) % p
    else:
        l = (((3 * x1 * x1 + a) % p) * gmpy2.invert(2 * y1, p)) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return [x3, y3]


# ECMH
def ECMH(data):
    Infinty = Add(0, 0, 0, 0)
    for item in data:
        item = sm3(item)  #都是字符串类型
        item = int(item, 16)
        item1 = (pow(item, 3) + a * item + b) % p
        item_y = QR(item1, int(p))
        Infinty = Add(Infinty[0], Infinty[1], item, item_y)
    return Infinty

def ECMH_ADD(data1, data2):
    data2 = sm3(data2[0])
    data2 = int(data2, 16)
    data2_x = (pow(data2, 3) + a * data2 + b) % p
    data2_y = QR(data2_x, p)
    result = Add(data1[0], data1[1], data2, data2_y)
    return result

def ECMH_REMOVE(data1, data2):
    data2 = sm3(data2[0])
    data2 = int(data2, 16)
    data2_x = (pow(data2, 3) + a * data2 + b) % p
    data2_y = QR(data2_x, p)
    result = Add(data1[0], data1[1], data2, p - data2_y)
    return result

#示例
str1 = ['ab46546464']
str2 = ['ab46546464', 'ab46546464']
str3 = ['123456ac757645ef5465', 'a5459645646acd354563d']
str4 = ['a5459645646acd354563d', '123456ac757645ef5465']
str5 = ['123456ac757645ef5465', 'a5459645646acd354563d', 'ab46546464']

strx = ['ab46546464', '3265752a23434c']
stry = ['3265752a23434c', 'ab46546464']
result1 = ECMH(str1)
result2 = ECMH(str2)
result3 = ECMH(str3)
result4 = ECMH(str4)
result5 = ECMH(str5)
print("第一个字符串集：", str1, '\n')
print("hash: ", result1, '\n')

print("第二个字符串集", str2, '\n')
print("hash: ", result2, '\n')

print("第三个字符串集", str3, '\n')
print("hash: ", result3, '\n')

print("第四个字符串集", str4, '\n')
print("hash: ", result4, '\n')

print("第五个字符串集", str5, '\n')
print("hash: ", result5, '\n')

if result1 != result2:
    print("由第一个和第二个字符串集的结果可知，Hash{a}不等于Hash{a, a}\n")

if result3 == result4:
    print("由第三个和第四个字符串集的结果可知，Hash{a， b}等于Hash{b, a}\n")


result6 = ECMH_ADD(result3, str1)
if result6 == result5:
    print("Hash{a, b} + Hash{c}: ", result6, '\n')
    print("Hash{a, b, c} = Hash{a, b} + Hash{c}: ", result5, '\n')
    print("由前两步得出Hash{a, b, c} = Hash{a, b} + Hash{c}\n")

result7 = ECMH_REMOVE(result5, str1)
if result7 == result3:
    print("Hash{a, b, c} - Hash{c}: ", result7, '\n')
    print("Hash{a, b} = Hash{a, b, c} - Hash{c}: ", result3, '\n')
    print("由前两步得出Hash{a, b} = Hash{a, b, c} - Hash{c}\n")


