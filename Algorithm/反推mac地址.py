import pandas as pd


def reverse(part_of_ip):
    '''
    EUI-64 逆转为mac地址
    '''
    x = int(part_of_ip, 16) # 16 -> 10
    b = bin(x)[2:] # 10 -> 2
    if len(b) < 8:
        b = (8 - len(b))*'0' + b
    b = list(b)

    # 翻转二进制的第七位
    if b[6] == '1':
        b[6] = '0'
    else:
        b[6] = '1'
    b = ''.join(b)

    t = int(b, 2) # 2 -> 10
    tt = hex(t)[2:]
    return tt

def get_mac(a, b):
    '''
    a: 前八位的第七位进行翻转后的16进制
    b: interface进过split(':')的列表
    '''
    first = a + b[0][2:]

    if b[1].endswith('ff') and b[2].startswith('fe'):
        second = b[1][:2] + b[2][2:]
    
    mac = ':'.join([first, second, b[-1]])

    return mac

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
    if ip.endswith('::'):
        ip = ip.replace('::', ':0000'*d)
    else:
        ip = ip.replace('::', ':0000'*d + ':')
    temp = ip.split(':')
    # print(temp)
    for index, i in enumerate(temp):
        l = len(i)
        if l < 4:
            d = 4 - l
            temp[index] = '0'*d + i

    return ':'.join(temp)

def find_error():
    path = r'C:\Users\Liang\Desktop\data\EUI-64.csv'
    df = pd.read_csv(path)
    # print(list(df['ip']))
    for i in list(df['ip']):
        x = replenish_ip(i)
        if x.rindex('ff:fe') == 27:
            pass
        else:
            print(f'error!!!-----   {x}')
        # print(x.rindex('ff:fe'))
    # print(df['ip'].str.rindex('ff:fe'))
if __name__ == "__main__":
    
    # with open('D:/eui_list.txt') as fp:
    #     lines = fp.read().split('\n')
    # error_list = []
    # for index_, i in enumerate(lines):
    #     if i == '':
    #         continue
    #     splited = i.split(':')[4:]
    #     # 补齐省略的前导0
    #     for index, j in enumerate(splited):
    #         l = len(j)
    #         if l < 4:
    #             splited[index] = (4 - l)*'0' + j
    #     print(splited)
    #     part_of_ip = splited[0][:2]
    #     try:
    #         print(get_mac(reverse(part_of_ip), splited))
    #     except:
    #         error_list.append((index_, i))
    # print(error_list)
    find_error()
