#coding=gbk
import hashlib
import math
def stb(string):
    bytes_obj = string.encode() # ת��Ϊ bytes ����
    #print(type(bytes_obj), bytes_obj)
    int_obj = int.from_bytes(bytes_obj, byteorder='big') # ת��Ϊ int ����
    #print(type(int_obj), int_obj)
    str_obj = bin(int_obj) # ת��Ϊ str ����
    #print(type(str_obj), str_obj)
    bin_str = str_obj.replace('0b', '') # ȥ��ǰ׺ '0b'
    str = bin_str.ljust(256, '0') # ���Ҳಹ�� 0
    #print( bin_str) 
    return str

#��ϣ����_����k������ʾ��ϣ��
def hash_encode(s,k):
    # ����һ��SHA-256��ϣ����
    m = hashlib.sha256()
        # ���ϣ�������������
    m.update(bxor(s,k).encode())
    # ��ȡ��ϣֵ
    h = m.digest()
    # ����ϣֵת��Ϊ16�����ַ���
    d = m.hexdigest()
    #��ӡ��ϣֵ��16����
    print("0x",d,"\n")
    return d

#��֤���� 0�� 1��
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
        str_obj = bin(num) # ת��Ϊ str ����
        #print(type(str_obj), str_obj)
        bin_str = str_obj.replace('0b', '') # ȥ��ǰ׺ '0b'
        bin_str = bin_str.rjust(256, '0') # ����ಹ�� 0
    else:
        num=-num-1
        str_obj = bin(num) # ת��Ϊ str ����
        #print(type(str_obj), str_obj)
        bin_str = str_obj.replace('0b', '') # ȥ��ǰ׺ '0b'
        bin_str = bin_str.rjust(256, '0') # ����ಹ�� 0
        bin_str = bin_str.replace('0', '3') 
        bin_str = bin_str.replace('1', '0') 
        bin_str = bin_str.replace('3', '1') 
    #print( bin_str) 
    return bin_str



def dec_to_binary(num,n):
    str_obj = bin(num)[2:] # ת��Ϊ str ����
    if len(str_obj)<n:
        str_obj=str_obj.rjust(n,'0')
    else:
        str_obj=str_obj[len(str_obj)-n:]
    print(str_obj)
    return str_obj
#�Ա����Ķ�����ж�����������
def bxor(s,k):
    str1 = s    
    str2 = k
    int1 = int(str1, 2) # ����һ���ַ���ת��Ϊ int ����
    int2 = int(str2, 2) # ���ڶ����ַ���ת��Ϊ int ����
    int3 = int1 ^ int2 # ������ int ���ͽ����������
    #print(type(int3), int3) 
    str3 = bin(int3)[2:] # �� int ����ת��Ϊ str ����
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


#��ϣ����Ҫ֤��������������[1:100]����Ϊ20
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
#�õ�h_i
for i in range(0,n):
    if b_x[i]=='0':
        k=2**i
    else:
        k=-2**i
    print(k)
    h_i.append(hash_encode(stb(seed),dtb(k)))
    k_i.append(k)

verif(seed,h_i,n,p)


