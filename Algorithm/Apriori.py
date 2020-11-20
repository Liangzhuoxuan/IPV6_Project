'''
1.找到频繁项集
2.发现关联规则

Apriori 参数: 最小支持度support, 数据集

概念：
项集：所有特征为1的值组成的集合

博客地址
https://ailearning.apachecn.org/#/docs/ml/11.%E4%BD%BF%E7%94%A8Apriori%E7%AE%97%E6%B3%95%E8%BF%9B%E8%A1%8C%E5%85%B3%E8%81%94%E5%88%86%E6%9E%90?id=%e4%b8%80%e4%b8%aa%e9%a2%91%e7%b9%81%e9%a1%b9%e9%9b%86%e5%8f%af%e4%bb%a5%e4%ba%a7%e7%94%9f%e5%a4%9a%e5%b0%91%e6%9d%a1%e5%85%b3%e8%81%94%e8%a7%84%e5%88%99%e5%91%a2%ef%bc%9f
https://blog.csdn.net/qq_36523839/article/details/82191677
https://blog.csdn.net/huguozhiengr/article/details/82869591
'''
from numpy import *
import csv


# todo:寻找频繁项集

# 加载数据集
def loadDataSet():
    return [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]


# 生成所有单个物品的项集列表
def creatC1(dataSet):
    '''
    dataSet 二维数组
    '''
    C1 = list()
    for transaction in dataSet:
        for item in transaction:
            if [item] not in C1:
                C1.append([item])
    C1.sort()

    # 使用frozenset为了后面可以将这些值作为字典的键
    return list(map(frozenset, C1))


# 过滤掉不符合最小支持度的集合
# 返回 频繁项集列表 retList, 所有元素的支持度子字典 
def scanD(D, Ck, minSupport):
    '''
    Arg:
        D:DataSet
        Ck:第k个候选项集 [{}, {}, {}]
        因为后面肯定是从候选项集1，即候选项集中每一项都是1个元素，
        到候选项集2，候选项集中每一项都是2个元素
    
    variable:
        ssCnt <dict> :计算候选项集中的每一项在数据集中出现的次数，后面用来计算 支持度support
        supportData <dict> :键为一个项集，值为该项集的支持度support
        retList <list> :将所有支持度大于阈值的项集即频繁项集保存到此列表 [{'a', 'b'}, {'a', 'c'}]

    return:
        retList
        supportData
    '''
    ssCnt = dict()
    # 把数据集和候选项集 Ck 的每一条数据进行逐一比对
    for tid in D:
        for can in Ck:
            # 判断子集
            if can.issubset(tid):
                if can not in ssCnt:
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1

    numItems = float(len(D))
    retList = []
    supportData = dict()
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.insert(0, key)
        supportData[key] = support
    return retList, supportData


# 将 L_{k-1} 的项集列表转换为 Lk 的项集列表
def aprioriGen(Lk, k):
    '''
    Arg:
        Lk 频繁项集列表  [{'a', 'b'}, {'a', 'c'}, {'b', 'c'}]
        k 项集元素的个数

    todo:
        从每个项集中元素个数为 k-1 个的候选项集，生成每个项集中元素个数为 k 个的候选项集

    attention:
        要生成Lk，要遍历 L_{k-1} 中的每个元素，两两进行并集操作，但是为了保证并集得到的集合的元素个数为 k 个，
        就要保证 L_{k-1} 中前 k-2 个元素都是相同的，如果不相同如 L3 中的一个 {'a', 'b', 'c} 和 L3 中的另一个
        {'b', 'f', 'd'} 就会生成一个 L5 的集合 {'a', 'b', 'c', 'd', 'f'}，而 {'a', 'b', 'c} 和 {'e', 'b', 'c}
        就能生成一个 L4 的集合 {'a', 'b', 'c', 'd'}，所以要对 L_{k-1} 中的前 k-2 个元素进行排序并比对
    '''
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk):
            L1 = list(Lk[i])[:k-2]
            L2 = list(Lk[j])[:k-2]
            L1.sort()
            L2.sort()
            if L1 == L2:
                # 求两者的并集
                retList.append(Lk[i] | Lk[j])
    return retList


def apriori(dataSet, minSupport=0.5):
    '''
    Arg：
        dataSet: 二维数组
        minSupport: 最小支持度

    variable:
        C: 项集列表，每一项为一个集合
        D: 对数据集<二维数组>的每一行进行集合处理
        L: 存储所有频繁项集的列表

    algorithm:
        从每一项为 1个元素的集合的候选集生成频繁项集，一直到 k个元素的集合的候选集生成频繁项集
        直到不能在生成频繁项集为止

    '''
    C1 = creatC1(dataSet)
    D = map(set, dataSet)
    print('D=', D)
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):
        print('k=', k, L, L[k-2])
        Ck = aprioriGen(L[k-2], k)
        print('Ck', Ck)

        Lk, supK = scanD(D, Ck, minSupport)
        supportData.update(supK)
        if len(Lk) == 0:
            break
        L.append(Lk)
        k += 1
    return L, supportData

# todo: 提取关联规则

def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    """calcConf（对两个元素的频繁项，计算可信度，例如： {1,2}/{1} 或者 {1,2}/{2} 看是否满足条件）

    Args:
        freqSet 频繁项集中的元素，例如: frozenset([1, 3])    
        H 频繁项集中的元素的集合，例如: [frozenset([1]), frozenset([3])]
        supportData 所有元素的支持度的字典
        brl即 bigrulelist 用来记录所有的关联规则[(freqSet-conseq, conseq, conf)]
        minConf 最小可信度
    Returns:
        prunedH 记录 可信度大于阈值的集合
    """
    prunedH = []
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet-conseq]
        if conf >= minConf:
            print(freqSet - conseq, '-->', conseq, 'conf:', conf)
            brl.append((freqSet-conseq, conseq, conf))
            prunedH.append(conseq)

    return prunedH # 满足最小置信度要求的每一项为单个元素的集合


def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    """rulesFromConseq

    Args:
        freqSet 频繁项集中的元素，例如: frozenset([2, 3, 5])    
        H 频繁项集中的元素的集合，例如: [frozenset([2]), frozenset([3]), frozenset([5])]
        supportData 所有元素的支持度的字典
        brl即 bigrulelist 用来记录所有的关联规则[(freqSet-conseq, conseq, conf)]
        minConf 最小可信度
    """
    # H[0] 是 freqSet 的元素组合的第一个元素，并且 H 中所有元素的长度都一样，长度由 aprioriGen(H, m+1) 这里的 m + 1 来控制
    # 该函数递归时，H[0] 的长度从 1 开始增长 1 2 3 ...
    # 假设 freqSet = frozenset([2, 3, 5]), H = [frozenset([2]), frozenset([3]), frozenset([5])]
    # 那么 m = len(H[0]) 的递归的值依次为 1 2
    # 在 m = 2 时, 跳出该递归。假设再递归一次，那么 H[0] = frozenset([2, 3, 5])，freqSet = frozenset([2, 3, 5]) ，没必要再计算 freqSet 与 H[0] 的关联规则了。
    m = len(H[0]) # 获得 Lk 的长度
    # 如果当前长度大于 Lk 的长度就不用在递归下去了
    if (len(freqSet) > (m + 1)):
        print('freqSet*******', len(freqSet), m+1, freqSet, H, H[0])
        Hmp1 = aprioriGen(H, m+1)
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        # 到最后穷举完所有的组合 len(Hmp1)就等于 1，剩下它自己了
        if(len(Hmp1) > 1):
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)


def generateRules(L, supportData, minConf=0.7):
    '''
    Arg:
        L: 频繁项集列表
    '''
    bigRuleList = []
    for i in range(1, len(L)):
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if (i > 1):
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList