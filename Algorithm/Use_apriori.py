import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from io import BytesIO
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules
from time import time
import logging


class FrequentPatternsIPv6(object):
    '''
    传入对应的两个ipv6切片，
    寻找这两个ipv6切片之间的关联规则
    '''

    def __init__(
            self, data_path, slice_ip_1_start, slice_ip_1_end,
            slice_ip_2_start, slice_ip_2_end
    ):
        assert (0 <= slice_ip_1_start <= 128 or 0 <= slice_ip_1_end <= 128 or
                0 <= slice_ip_2_start <= 128 or 0 <= slice_ip_2_end <= 128), \
            'please input the correct slice'
        # 平时说的ip都是从 1 开始数的，字符串是从 0 开始数的
        slice_ip_1_start -= 1
        slice_ip_1_end -= 1
        slice_ip_2_start -= 1
        slice_ip_2_end -= 1
        self.slice_ip_1 = str(slice_ip_1_start) + ':' + str(slice_ip_1_end)
        self.slice_ip_2 = str(slice_ip_2_start) + ':' + str(slice_ip_2_end)
        self.slice_ip_1_start = slice_ip_1_start
        self.slice_ip_1_end = slice_ip_1_end
        self.slice_ip_2_start = slice_ip_2_start
        self.slice_ip_2_end = slice_ip_2_end
        self.path = data_path

        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(asctime)s:\n %(message)s',
            filename='logging_.txt', 
            filemode='a',
        )
        logging.debug('debug message of running')

    def load_data(self):
        '''
        数据格式
        ip      label
        ...     ...
        ...     ...
        ...     ...

        默认 DHCP 的标签为 0
        '''
        return pd.read_csv(self.path)

    def replenish_ip(self, ip):
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
            ip = ip.replace('::', ':0000' * d)
        else:
            # 对于末尾为 :: 的 ip也要补全 0
            ip = ip.replace('::', ':0000' * d + ':')
        _temp = ip.split(':')
        for index, i in enumerate(_temp):
            l = len(i)
            if l < 4:
                d = 4 - l
                _temp[index] = '0' * d + i

        return ':'.join(_temp)

    def hex_to_bin(self, ip, flag, slice_here):
        '''
        十六进制转二进制
        flag: 1 表示处理的是输入的第一个ip切片索引
        '''
        # 排除奇奇怪怪的东西 "2.at.pool.ntp.org", '[2a0a' 这样的东西
        if ':' not in ip or '[' in ip:
            return 'error_ip'  # 记住在进行apply完之后要检查一遍 'error_ip'
        ip = self.replenish_ip(ip)
        ip = ip.split(':')
        memory_list = []
        for i in ip:
            temp__ = int(i, 16)
            b = bin(temp__)[2:]
            x = len(b)
            if x < 16:
                d = 16 - x
                b = '0' * d + b
            memory_list.append(b)
        final = ''.join(memory_list)

        start, stop = slice_here.split(':')
        return final[int(start): int(stop)]

    def bin_to_hex(self, string):
        '''
        二进制转十六进制
        '''
        demical = int(string, 2)
        return hex(demical)[2:]

    def clean_data(self):
        '''
        数据清洗
        :return: 经过数据清洗后两个ipv6切片的 Series
        '''
        df = self.load_data()
        df = df[df['label'] == 0]  # 选出 DHCP
        temp = df['ip']
        temp_1 = temp.apply(self.hex_to_bin, args=(1, self.slice_ip_1))
        error_ip_num = temp_1[temp_1 == 'error_ip'].count()
        logging.debug(f'数据集中的异常ip数量为{error_ip_num}条\n')
        print(f'数据集中的异常ip数量为{error_ip_num}条')
        print('\n\n', '**'*30)

        err_index = temp_1[temp_1 == 'error_ip'].index
        temp_1.drop(index=err_index, inplace=True)
        pickle_name_1 = f'./from_{self.slice_ip_1_start}_to_{self.slice_ip_1_end}_first.pk'
        temp_1.to_pickle(pickle_name_1)

        temp_2 = temp.apply(self.hex_to_bin, args=(2, self.slice_ip_2))
        err_index = temp_2[temp_2 == 'error_ip'].index
        temp_2.drop(index=err_index, inplace=True)
        pickle_name_2 = f'./from_{self.slice_ip_2_start}_to_{self.slice_ip_2_end}_second.pk'
        temp_2.to_pickle(pickle_name_2)

        return temp_1, temp_2

    def slice_ipv6_describe(self):
        '''
        这个ip切片的统计信息：
        各个切片的占比
        '''
        series_1, series_2 = self.clean_data()

        def format_1(arg):
            x = len(arg)
            if x < 16:
                arg = '0'*(16 - x) + arg
            return arg

        def format_2(arg):
            x = len(arg)
            if x < 8:
                arg = '0'*(8 - x) + arg
            return arg
            
        series_1 = series_1.apply(format_1)
        series_2 = series_2.apply(format_2)     

        info_1 = series_1.value_counts() / series_1.count()
        info_2 = series_2.value_counts() / series_2.count()

        print(info_1)
        logging.debug(f'第{self.slice_ip_1_start + 1}位到第{self.slice_ip_1_end + 1}位的统计信息:\n')
        logging.debug(info_1)
        logging.debug('\n')
        print('\n\n', '**'*30)
        logging.debug(f'第{self.slice_ip_2_start + 1}位到第{self.slice_ip_2_end + 1}位的统计信息:')
        logging.debug(info_2)
        logging.debug('\n')
        print(info_2)

        series_1 = series_1.apply(self.bin_to_hex)
        series_2 = series_2.apply(self.bin_to_hex)

        # 补齐前导零
        def format_series_1(arg):
            l = len(arg)
            if l < 4:
                return '0' * (4 - l) + arg
            return arg

        def format_series_2(arg):
            if len(arg) == 1:
                return '0' + arg
            return arg

        series_1 = series_1.apply(format_series_1)
        series_2 = series_2.apply(format_series_2)

        return series_1, series_2

    def frequent_patterns_prepare(self, min_threshold=1000):
        '''
        Arg:
            min_thresshold: ip切片计数最小的阈值
        
        attention:
            当直接使用TransactionEncoder的时候，np.zeros()由于无法生成过大维度的数组会报错：
            Unable to allocate array with shape (1994891, 44205) and data type bool
            44205 = 104-120 的 unique值 + 120-128的 unique值，所以为了使用TransactionEncoder，要先除去support很小的值

            对于numpy的内存问题，在 linux上面跑的时候，并没有windows的这个限制，windows最大的m*n是10亿
        '''
        columns = [self.slice_ip_1, self.slice_ip_2]
        series_1, series_2 = self.slice_ipv6_describe()
        df = pd.DataFrame(list(zip(series_1, series_2)), columns=columns)

        # 获得 ip切片计数大于阈值的所有 ip切片的索引
        indices = series_1.value_counts()[series_1.value_counts() > min_threshold].index

        def filter_value(value):
            '''
            找出次数 >min_threshold 的对应的 df 切片
            不符合的标记为 冗余 'verbose'
            '''
            return value if value in indices else 'verbose'

        slice_df = df[self.slice_ip_1].apply(filter_value)

        # 把去除了冗余数据之后的 series 代替原来的 series，会产生很多 NaN，就是那些原本不对的数据
        df[self.slice_ip_1] = slice_df[slice_df != 'verbose']
        df.dropna(inplace=True)

        return df

    def apply_(self):
        df_ = self.frequent_patterns_prepare(min_threshold=1000)
        te = TransactionEncoder()  # 对数据集进行TransactionEncoder编码 
        df_tf = te.fit_transform(df_.values)

        df = pd.DataFrame(df_tf, columns=te.columns_)

        start = time()
        # 寻找频繁项集
        frequent_itemsets = fpgrowth(df, min_support=0.05, use_colnames=True)
        logging.debug('寻找频繁项集算法时耗:%s\n' % (time() - start))
        print('寻找频繁项集算法时耗:', time() - start)
        print()

        frequent_itemsets.sort_values(by='support', ascending=False, inplace=True)
        logging.debug(f'freqSet:\n{frequent_itemsets}\n')
        print(f'freqSet:\n{frequent_itemsets}')
        print('\n\n', '**'*30)

        # 生成关联规则
        association_rule = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.7)  # 指标为置信度
        association_rule.sort_values(by='leverage', ascending=False, inplace=True)  # 关联规则按leverage排序

        logging.debug('关联规则：\n{}'.format(association_rule))
        print('关联规则：\n{}'.format(association_rule))


if __name__ == "__main__":
    start = time()
    
    for i, j in zip(range(32, 64, 16), range(48, 81, 16)):
        print(i, j)
        fq_ = FrequentPatternsIPv6('D:/ipv6_label_lzx20190904.csv', i, j, 120, 128)
        fq_.apply_()

    for i, j in zip(range(32, 64, 8), range(40, 72, 8)):
        print(i, j)
        fq_ = FrequentPatternsIPv6('D:/ipv6_label_lzx20190904.csv', i, j, 120, 128)
        fq_.apply_()

    end = time()
    d = end - start
    min_ = d // 60
    s = d % 60
    print(f'{min_}min{s}s')