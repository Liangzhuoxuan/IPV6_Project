import numpy as np
import pandas as pd
from sklearn.cluster import Kmeans


def replenish_ip(ip):
    '''
    补全ip中的 :: 为0000
    补全ip中前导0的省略
    '''
    org_length = 8
    splited_ = ip.split(':')
    if '' in splited_:
        length = len(splited_) - 1
    else:
        length = len(splited_)
    d = org_length - length
    ip = ip.replace('::', ':0000'*d + ':')
    temp = ip.split(':')[4:]
    print(temp)
    for index, i in enumerate(temp):
        l = len(i)
        if l < 4:
            d = 4 - l
            temp[index] = '0'*d + i

    return ''.join(temp)


def read_file_to_mat(path='D:/responsive-addresses.txt/responsive-addresses.txt', n_iter=10000):
    '''
    path 文件路径
    n_iter 最大的读取行数
    '''
    f = open(path)
    line = f.readline()

    memory_ = []

    for i in range(n_iter):
        ip = f.readline().strip()
        if 'ff:fe' in ip: # 去掉 EUI-64 的类型
            continue
        temp = list(replenish_ip(ip))
        for k,j in enumerate(temp):
            if j == 'a':
                temp[k] = '11'
            elif j == 'b':
                temp[k] = '12'
            elif j == 'c':
                temp[k] = '13'
            elif j == 'd':
                temp[k] = '14'    
            elif j == 'e':
                temp[k] = '15'
            elif j == 'f':
                temp[k] = '16'
        memory_.append(temp) # 合并为二维数组
        
    return memory_

temp = read_file_to_mat(n_iter=100000)
df = pd.DataFrame(temp)
# temp


def reverse_from_df():
#     assert (self.df is None), 'df is None'
    def translate(number):
        if int(number) < 11:
            return number
        map_list1 = list(range(11, 16))
        map_list2 = ['a', 'b', 'c', 'd', 'e', 'f']
        index = map_list1.index(int(number))
        real = map_list2[index]
        return real

    index_ = df.iloc[_label == 0,:].index
    memory_list = []

    for index, i in enumerate(index_):
        s = df.iloc[i,:]
        a, b, c, d = ('', '', '', '')
        # 都得反向 translate一下
        for j in range(0, 4):
            a += translate(s[j])
        for k in range(4, 8):
            b += translate(s[k])
        for l in range(8, 12):
            c += translate(s[l])
        for m in range(12, 16):
            d += translate(s[m])
        print(a + ':' + b + ':' + c + ':' + d)
#         if index == 4:
#             break
