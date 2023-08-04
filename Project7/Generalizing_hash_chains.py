#coding=gbk
import hashlib
import math
def stb(string):
    bytes_obj = string.encode() # 转换为 bytes 类型
    #print(type(bytes_obj), bytes_obj)
    int_obj = int.from_bytes(bytes_obj, byteorder='big') # 转换为 int 类型
    #print(type(int_obj), int_obj)
    str_obj = bin(int_obj) # 转换为 str 类型
    #print(type(str_obj), str_obj)
    bin_str = str_obj.replace('0b', '') # 去掉前缀 '0b'
    str = bin_str.ljust(256, '0') # 在右侧补足 0
    #print( bin_str) 
    return str

#哈希函数_参数k用来表示哈希族
def hash_encode(s,k):
    # 创建一个SHA-256哈希对象
    m = hashlib.sha256()
        # 向哈希对象中添加数据
    m.update(bxor(s,k).encode())
    # 获取哈希值
    h = m.digest()
    # 将哈希值转换为16进制字符串
    d = m.hexdigest()
    #打印哈希值的16进制
    print("0x",d,"\n")
    return d

#验证函数 0对 1错
def hash_verif(s,d_,k):
    d=hash_encode(stb(s),dtb(k))
    if d==d_:
        print("The string matches the hash.")
        return 0
    else:
        print("The string does not match the hash.")
        return 1


def dtb(num):
    if num>=0:
        str_obj = bin(num) # 转换为 str 类型
        #print(type(str_obj), str_obj)
        bin_str = str_obj.replace('0b', '') # 去掉前缀 '0b'
        bin_str = bin_str.rjust(256, '0') # 在左侧补足 0
    else:
        num=-num-1
        str_obj = bin(num) # 转换为 str 类型
        #print(type(str_obj), str_obj)
        bin_str = str_obj.replace('0b', '') # 去掉前缀 '0b'
        bin_str = bin_str.rjust(256, '0') # 在左侧补足 0
        bin_str = bin_str.replace('0', '3') 
        bin_str = bin_str.replace('1', '0') 
        bin_str = bin_str.replace('3', '1') 
    #print( bin_str) 
    return bin_str



def dec_to_binary(num,n):
    str_obj = bin(num)[2:] # 转换为 str 类型
    if len(str_obj)<n:
        str_obj=str_obj.rjust(n,'0')
    else:
        str_obj=str_obj[len(str_obj)-n:]
    print(str_obj)
    return str_obj
#对编码后的对象进行对齐的异或运算
def bxor(s,k):
    str1 = s    
    str2 = k
    int1 = int(str1, 2) # 将第一个字符串转换为 int 类型
    int2 = int(str2, 2) # 将第二个字符串转换为 int 类型
    int3 = int1 ^ int2 # 对两个 int 类型进行异或运算
    #print(type(int3), int3) 
    str3 = bin(int3)[2:] # 将 int 类型转换为 str 类型
    str3=str3.rjust(256,'0')
    #print(str3)
    return str3

def verif(s,h_i,n,num):
    p=[]
    verif_num=0
    for i in range(0,n):
        k=2**i
        print(k)
        a=hash_verif(s,h_i[i],k)
        verif_num+=a*2**(n-i-1)
        if num==verif_num:
            print("Success!")


#哈希链想要证明所给的数属于[1:100]，数为20
seed="Hello World!"
a=1
b=100
l=b-a+1
c=20
p=c-a+1
n=math.log(l,2)
if n>n//1:
    n=int(n//1)+1
b_x=dec_to_binary(p,n)


k_i=[]
h_i=[]
#得到h_i
for i in range(0,n):
    if b_x[i]=='0':
        k=2**i
    else:
        k=-2**i
    print(k)
    h_i.append(hash_encode(stb(seed),dtb(k)))
    k_i.append(k)

verif(seed,h_i,n,p)


