#other pitfalls:
#leaking k
#reusing k
#same d and k with ECDSA
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
    #do sth
    return "".join(res)
    
#国密sm3加密
def sm3_hash(message):
    #do sth
    return hash_hex

# 定义点加
def Add(x1, y1, x2, y2):
    #do sth
    return x3, y3

# 定义点乘
def Mul_Add(x, y, n):
    #do sth
    return (qx, qy)

def KDF(xy, klen):
    #do sth
    return t[:klen]

# 签名函数
def Sm2Sign(m, ID, private_key):
    #do sth
    return r, s

def ECDSA(m, ID, private_key):
    #do sth
    return r, s

# leaking k
def LeakingK():
    r,s = Sm2Sign(m, ID, d)
    da = gmpy2.invert(s + r,n)
    da = da * (k - s)%n
    return da

#reusing k
def ResusingK():
     r1,s1 = Sm2Sign(Ma, ID, d)
      r2,s2 = Sm2Sign(Mb, ID, d)
    temp = s1-s2+r1-r2
    da = gmpy2.invert(temp,n)
    da = da * (s2-s1)%n

#same d and k with ECDSA
def SameDKECDSA():
     r1,s1 = Sm2Sign(m, ID, d)
      r2,s2 = ECDSA(m, ID, d)
      temp = r1-s1*s2-s1*r1
      da =  gmpy2.invert(temp,n)
      da = da*(s1*s2-e1)%n




















    
