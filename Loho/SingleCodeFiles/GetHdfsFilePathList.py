# !/usr/bin/env python3

# 大数据迁移，先获取到 HDFS 上的文件结构，然后判断结构中那些是需要拷贝的
# 按照日期指定，筛选出需要拷贝的文件夹，每一个文件夹单独进行 distcp 命令
import pyhdfs
from pyhdfs import HdfsClient
import os
import datetime
import time
import re


# 写文件
def writeFileWithStr(filePath_, str_):
    if not os.path.exists(os.path.dirname(filePath_)):
        os.makedirs(os.path.dirname(filePath_))
    try:
        _file = open(filePath_, 'w')
        try:
            _file.write(str_)
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)


def getClient(url_: str, userName_: str):
    return pyhdfs.HdfsClient(hosts=url_, user_name=userName_)


def listToStr(list_: list):
    _listStr = ""
    for _i in range(len(list_)):
        _filePath = list_[_i]
        _listStr += _filePath + "\n"
    _listStr = _listStr[:-1]
    return _listStr


# 显示文件夹结构
def showAllFolderHaveData(client_: HdfsClient, path_: str):
    _folderPathList = []
    for _root, _dir, _files in client_.walk(path_, status=True):
        # 有文件的内容的文件夹才是需要拷贝的文件夹
        if len(_files) > 0:
            print(_root)
            _folderPathList.append(_root)
    return listToStr(_folderPathList)


def readFromFile(filePath_):
    _contentStr = None
    try:
        _file = open(filePath_, 'r')
        try:
            _contentStr = _file.read()
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)
    return _contentStr


def datetimeToStr(datetime_, format_: str = None):
    _format = "%Y-%m-%d %H:%M:%S"
    if format_:
        _format = format_
    return datetime_.strftime(_format)


def getDaysBetween(beginDay_: str, endDay_: str):
    _dayStrList = []
    _datetimeList = devideTwoDatetimeIntoList(
        strToDatetime(beginDay_ + " 00:00:00"),
        strToDatetime(endDay_ + " 00:00:00"),
        datetime.timedelta(days=1)
    )
    for _i in range(len(_datetimeList)):
        _datetime = _datetimeList[_i]
        _dayStrList.append(datetimeToStr(_datetime, "%Y-%m-%d"))
    return _dayStrList


def strToDatetime(str_: str, format_: str = None):
    _format = "%Y-%m-%d %H:%M:%S"
    if format_:
        _format = format_
    _timeArray = time.strptime(str_, _format)
    return datetime.datetime(*_timeArray[0:6])


def compareDatetime(datetime1_, datetime2_):
    return compareTimeStr(datetimeToStr(datetime1_), datetimeToStr(datetime2_))


def compareTimeStr(timeStr1_, timeStr2_):
    _reg1 = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', timeStr1_)
    _reg2 = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', timeStr2_)
    if _reg1 and _reg2:
        return timeStr1_ > timeStr2_
    else:
        return None


def devideTwoDatetimeIntoList(datetime1_, datetime2_, datetimeTimedelta_):
    _datetimeList = [datetime1_, datetime1_ + datetimeTimedelta_]
    while not compareDatetime(_datetimeList[len(_datetimeList) - 1], datetime2_):
        _datetimeList.append(_datetimeList[-1] + datetimeTimedelta_)
    _datetimeList = _datetimeList[:-1]
    return _datetimeList


def createCmdByDay(dayStrList_: list, distcpTemplete_: str, folderPathFile_: str, cmdFileSaveFolder_: str):
    # 制作每一天的distcp脚本
    _folderPathListStr = readFromFile(folderPathFile_)
    _folderPathList = _folderPathListStr.split("\n")
    for _i in range(len(dayStrList_)):
        _dayStr = dayStrList_[_i]
        _cmdStr = ""
        _count = 0
        for _j in range(len(_folderPathList)):
            _folderPath = _folderPathList[_j]
            _regDayStr = re.search('.*' + _dayStr, _folderPath)
            # 日期匹配，这个目录就为目标目录
            if _regDayStr:
                _cmd = distcpTemplete_.format(targetFolder=_folderPath)
                _cmdStr = _cmdStr + "echo " + str(_count + 1) + "\n" + _cmd + "\n"
                _count = _count + 1
        # 有需要拷贝的文件那么就生成一个cmd脚本文件
        if not _cmdStr == "":
            writeFileWithStr(
                cmdFileSaveFolder_ + _dayStr + ".sh",
                _cmdStr
            )


def createCmdByFolder(distcpTemplete_: str, folderPathFile_: str, cmdFileSaveFolder_: str):
    _folderPathListStr = readFromFile(folderPathFile_)
    _folderPathList = _folderPathListStr.split("\n")
    _parentFolderPathList = []
    for _i in range(len(_folderPathList)):
        _folderPath = _folderPathList[_i]
        _regFolderPath = re.search('(.*)\d*-\d*-\d*', _folderPath)
        if _regFolderPath:
            _parentFolderPath = _regFolderPath.group(1)
            if not _parentFolderPath in _parentFolderPathList:
                _parentFolderPathList.append(_parentFolderPath)
    _cmdStr = ""
    for _i in range(len(_parentFolderPathList)):
        _parentFolderPath = _parentFolderPathList[_i]
        _cmd = distcpTemplete_.format(targetFolder=_parentFolderPath)
        _cmdStr = _cmdStr + "echo " + str(_i + 1) + "\n" + _cmd + "\n"

    writeFileWithStr(
        cmdFileSaveFolder_ + "folderList.sh",
        _cmdStr
    )


if __name__ == "__main__":
    # 腾讯
    _client = getClient("ip:port", "hadoop")
    # cmd 模板
    _distcpTemplete = 'hadoop distcp -pbugpc -i -update -m36 -bandwidth 30 hdfs://ip:port{targetFolder} {targetFolder}'

    # ------------------------------------------------------------------------------------------------------------------
    # 从HDFS获取要拷贝的文件路径信息
    # # ODS数据路径
    # writeFileWithStr(
    #     "/tmp/ods/thirtyParty/ods",
    #     showAllFolderHaveData(_client, "/usr/hive/warehouse/ods.db/")
    # )

    # # H5数据路径
    # writeFileWithStr(
    #     "/tmp/ods/thirtyParty/h5",
    #     showAllFolderHaveData(_client, "/original_data/kod/h5/")
    # )

    # ------------------------------------------------------------------------------------------------------------------
    # 将同一天的路径都取出来，然后，创建cmd命令
    # 从 2016 年开始 到 2019 年 3月
    _dayStrList = getDaysBetween("2016-09-01", "2019-03-01")
    # 生成执行的sh脚本
    createCmdByDay(_dayStrList, _distcpTemplete, "/tmp/ods/thirtyParty/ods", "/tmp/ods/thirtyParty/cmds/ods/")
    createCmdByDay(_dayStrList, _distcpTemplete, "/tmp/ods/thirtyParty/h5", "/tmp/ods/thirtyParty/cmds/h5/")

    # ------------------------------------------------------------------------------------------------------------------
    # # 将不同名称<库>和<库+id>取出来
    # createCmdByFolder(_distcpTemplete, "/tmp/ods/thirtyParty/ods", "/tmp/ods/thirtyParty/folderCmds/ods/")
    # createCmdByFolder(_distcpTemplete, "/tmp/ods/thirtyParty/h5", "/tmp/ods/thirtyParty/folderCmds/h5/")
