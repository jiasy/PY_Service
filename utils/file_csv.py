# !/usr/bin/env python3
# csv 文件读写
import csv
import json
import os

# dict 字典 构成的列表，选取其中的几个字段，写入文件
from pyspark import SparkConf, SparkContext, SQLContext


def getSQLContext():
    _clusterType = "local"
    _conf = SparkConf().setMaster(_clusterType).setAppName("csvUse")
    _sc = SparkContext(conf=_conf)
    _sqlCtx = SQLContext(_sc)
    return _sqlCtx


# 字典构成的列表写入 csv 文件
def writeListOfDictToCSV(filePath_: str, listOfDict_: list, keys_: list = None):
    _fieldnames = keys_
    # 有指定的keys就写入指定的
    if not _fieldnames:
        # 没有就全写，先得到键的并集，然后在写
        _keySet = set([])
        for _dict in listOfDict_:
            # 每一元素的keys进行并集操作
            _keySet = _keySet | set(_dict.keys())
        _fieldnames = list(_keySet)

    # 开始写入文件
    with open(filePath_, 'w') as _csvFile:
        _writer = csv.DictWriter(_csvFile, fieldnames=_fieldnames)
        for _dict in listOfDict_:
            _writer.writerow(_dict)


# 读取数据
def readListOfDictFromCSV(filePath_: str, splitStr_: str = ","):
    _listOfDict = []
    with open(filePath_, 'r') as _csvFile:
        _reader = csv.DictReader(_csvFile, delimiter=splitStr_)
        for _dict in _reader:
            _listOfDict.append(_dict)
    return _listOfDict


# 将矩阵写入CSV中
def writeMatrixToCSV(filePath_: str, matrixList_: list, splitStr_: str = ","):
    with open(filePath_, 'w') as _csvFile:
        _writer = csv.writer(_csvFile, delimiter=splitStr_)
        # for _row in matrixList_:
        #     _writer.writerow(_row)
        _writer.writerows(matrixList_)


# 将矩阵写入CSV中
def readMatrixFromCSV(filePath_: str, splitStr_: str = ","):
    _matrix = []
    with open(filePath_, 'r') as _csvFile:
        _read = csv.reader(_csvFile, delimiter=splitStr_)
        for _row in _read:
            _matrix.append(_row)

    return _matrix


if __name__ == "__main__":
    print("")
