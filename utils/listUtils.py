#!/usr/bin/env python3
import numpy as np


# 模拟shift
def list_shift(list_):
    return list_.pop(0)


# 模拟pop
def list_pop(list_):
    return list_.pop(len(list_) - 1)


def getValueListFromDictObject(dictObject_: dict):
    return [_value for _, _value in dictObject_.items()]

'''
_sourceStrList = [
    "+ - - * / // ** %"
    ,
    "np.add np.subtract np.negative np.multiply np.divide np.floor_divide np.power np.mod"
    ,
    "加法运算(即1+1=2) 减法运算(即3-2=1) 负数运算(即-2) 乘法运算(即2*3=6) 除法运算(即3/2=1.5) 地板除法运算(ﬂoor，division，即3//2=1) 指数运算(即2**3=8) 模/余数(即9%4=1)"
]
_list = [_str.split(" ") for _str in _sourceStrList]
_list = listUtils.transpose(_list)
for _strList in _list:
    print(_strList[0].ljust(5) + " " + _strList[1].ljust(15) + " " + _strList[2])
'''


# 二维数组转置
def transpose(list_: list):
    return list(map(list, zip(*list_)))


# 利用np进行数组转置，指定类型为 O，代表元素为Python对象。<对象的转置，反而没有以上的实现快>
def npTranspose(list_: list):
    _list = np.array(list_, dtype="O")
    return _list.T


# 字典对象构成的列表，按照对象的某一个key进行排序，默认升序
def sortListOfDict(list_: list, sortKey_: str, reverse_: bool = False):
    # 排序的结果非期望的时候，查证一下key对应的是不是数字
    list_.sort(key=lambda _info: _info.get(sortKey_), reverse=reverse_)


# 两个列表去重合并
def unionTwoList(listA_: list, listB_: list):
    return list(set(listA_).union(set(listB_)))


# 将每个元素链接起来，形成字符串
def joinListToStr(list_: list, joinStr_: str):
    return joinStr_.join(list_)


# 打印列表
def printList(list_: list, prefix_: str = ""):
    for _i in range(len(list_)):
        print(prefix_ + str(list_[_i]))


# 找到并移除
def findAndRemove(list_: list, element_):
    if element_ in list_:
        list_.pop(list_.index(element_))
        return True
    else:
        return False
