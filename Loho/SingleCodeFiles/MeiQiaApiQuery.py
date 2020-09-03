# !/usr/bin/env python3

import json
import requests
import re
import datetime
import time
import os
import getopt
import sys
import pyhdfs
import shutil


def requestApi(url_: str):
    r = requests.get(url_)

    response_dict = r.json()
    return response_dict


def getRequestApiUrl(url_: str, api_: str, paramDict_: dict):
    _url = url_.strip()
    if not _url[-1::] == "/":
        _url = _url + "/"
    _api = api_.strip()
    _paramList = []
    for _key in paramDict_:
        _paramList.append(_key + "=" + str(paramDict_[_key]))
    _finallUrl = _url + _api + "?" + "&".join(_paramList)
    return _finallUrl


def strToDatetime(str_: str, format_: str = None):
    _format = "%Y-%m-%d %H:%M:%S"
    if format_:
        _format = format_
    _timeArray = time.strptime(str_, _format)
    return datetime.datetime(*_timeArray[0:6])


def datetimeToStr(datetime_, format_: str = None):
    _format = "%Y-%m-%d %H:%M:%S"
    if format_:
        _format = format_
    return datetime_.strftime(_format)


def compareDatetime(datetime1_, datetime2_):
    return compareTimeStr(datetimeToStr(datetime1_), datetimeToStr(datetime2_))


# 比较时间
def compareTimeStr(timeStr1_, timeStr2_):
    _reg1 = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', timeStr1_)
    _reg2 = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', timeStr2_)
    if _reg1 and _reg2:
        return timeStr1_ > timeStr2_
    else:
        return None


# 等分两个时间点
def devideTwoDatetimeIntoList(datetime1_, datetime2_, datetimeTimedelta_):
    _datetimeList = [datetime1_, datetime1_ + datetimeTimedelta_]
    while not compareDatetime(_datetimeList[len(_datetimeList) - 1], datetime2_):
        _datetimeList.append(_datetimeList[-1] + datetimeTimedelta_)
    _datetimeList.pop(len(_datetimeList) - 1)
    return _datetimeList


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
    if userName_:
        return pyhdfs.HdfsClient(hosts=url_, user_name=userName_)
    else:
        return pyhdfs.HdfsClient(hosts=url_)


def timestampToDatetime(ts_):
    return datetime.datetime.fromtimestamp(ts_)


def datetimeToTimestamp(datetime_):
    return datetime_.timestamp()


def requestMeiQiaList(beginDay_, beginTime_, endDay_, endTime_, paramJsonStr_, type_):
    if not (type_ == "tickets" or type_ == "conversations"):
        return []
    # 设置其实时间和结束时间
    _timeDict = dict({})
    _timeDict["beginDay"] = beginDay_
    _timeDict["beginTime"] = beginTime_
    _timeDict["endDay"] = endDay_
    _timeDict["endTime"] = endTime_
    _paramDict = json.loads(paramJsonStr_.format(**_timeDict))
    _apiUrl = getRequestApiUrl("https://api.meiqia.com/v1", type_, _paramDict)

    # 获取列表
    def _getList(apiUrlInside_):
        _apiResultDict = requestApi(apiUrlInside_)
        _listInside = _apiResultDict["result"]
        return _listInside

    # 重试次数
    _recount = 0
    _list = _getList(_apiUrl)
    # 结果为空，且重试没超过3次
    while (_list is None and _recount < 3):
        _list = _getList(_apiUrl)
        _recount = _recount + 1

    if _recount == 3:
        print(_apiUrl + "\n" + "重试次数超过三次依然没有得到结果")
        sys.exit(1)

    return _list


# 获取文件列表
def getFilterFilesInPath(path_):
    _allFilePaths = []
    for root, dirs, files in os.walk(path_):
        _realFilePaths = [os.path.join(root, _file) for _file in files]
        _allFilePaths = _allFilePaths + _realFilePaths
    return _allFilePaths


# 以某一天为基准
def getDayFromTargetDay(targetDateTime_, bufferDay_: int):
    _realDay = targetDateTime_ + datetime.timedelta(days=bufferDay_)
    return _realDay.strftime("%Y-%m-%d %H:%M:%S")


# 将起止时间作为参数，传递给脚本 注意时间格式中空格需要加'\'
# python3 MeiQiaApiQuery.py -s 2019-02-14\ 06 -e 2019-02-14\ 06 -t /tmp/ods/thirtyParty/meiQiaTmpFile -u hadoop-1.loho.local -n hadoop -f /ods/thirtyParty/meiQia -w conversations
# python3 MeiQiaApiQuery.py -s 2019-02-14\ 06 -e 2019-02-14\ 12 -t /tmp/ods/thirtyParty/meiQiaTmpFile -u hadoop-1.loho.local -n hadoop -f /ods/thirtyParty/meiQia -w tickets
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "hs:e:t:u:n:f:w:")
    _start = None
    _end = None

    # 临时文件保存目录
    _tempFilePath = None
    # hdfs地址
    _hdfsUrl = None
    # hdfs用户
    _hdfsUserName = None
    # hdfs目标路径
    _hdfsTargetFolder = None
    # 查询那个API
    _which = None
    # 起止时间
    _beginDay = "2019-02-14"
    _beginTime = "06"
    _endDay = "2019-02-14"
    _endTime = "12"
    for _op, _value in opts:
        if _op == "-s":
            _start = _value
            _beginDay = _start.split(" ")[0]
            _beginTime = _start.split(" ")[1] + ":00:00"
        if _op == "-e":
            _end = _value
            _endDay = _end.split(" ")[0]
            _endTime = _end.split(" ")[1] + ":00:00"
        if _op == "-t":
            _tempFilePath = _value
        if _op == "-u":
            _hdfsUrl = _value
        # if _op == "-n":
        #     _hdfsUserName = _value
        if _op == "-f":
            _hdfsTargetFolder = _value
        if _op == "-w":
            _which = _value

    if not _which or not _start or not _end or not _hdfsUrl or not _hdfsTargetFolder or not _tempFilePath:
        print("有参数空了")
        sys.exit(1)

    # hdfs 的截止时间作为目录
    _hdfsTargetFolder = _hdfsTargetFolder

    _templeteJsonStr_conv = \
        """
    {{
      "conv_start_from_tm": "{beginDay}+{beginTime}",
      "conv_start_to_tm": "{endDay}+{endTime}",
      "offset": 0,
      "limit": 20,
      "app_id": "appId",
      "sign": "signToken",
      "enterprise_id": "00000"
    }}
        """

    _templeteJsonStr_ticket = \
        """
    {{
      "ticket_start_from_tm": "{beginDay}+{beginTime}",
      "ticket_start_to_tm": "{endDay}+{endTime}",
      "offset": 0,
      "limit": 20,
      "app_id": "appId",
      "sign": "signToken",
      "enterprise_id": "00000"
    }}
        """
    _templeteJsonStr = ""
    if _which == "tickets":
        _templeteJsonStr = _templeteJsonStr_ticket
    elif _which == "conversations":
        _templeteJsonStr = _templeteJsonStr_conv

    # 转换起止时间
    _begindDateTime = strToDatetime(_beginDay + " " + _beginTime)
    _endDateTime = strToDatetime(_endDay + " " + _endTime)
    # 1小时为间隔分割是时间段,美洽的时间段支持最大支持12小时
    _timeList = devideTwoDatetimeIntoList(_begindDateTime, _endDateTime, datetime.timedelta(hours=1))
    _timeStrList = [datetimeToStr(_time) for _time in _timeList]
    # 最后一项时间小于截止时间的时候，把截止时间添加到最后
    if datetimeToStr(_endDateTime) > _timeStrList[-1]:
        _timeStrList.append(datetimeToStr(_endDateTime))

    for _i in range(len(_timeStrList) - 1):
        # 最终结果数组
        _finallList = []

        # 前一项做为起始时间，后一项作为结束时间，进行数据获取
        _begin = _timeStrList[_i]
        _end = _timeStrList[_i + 1]
        _beginTimeStrList = _begin.split(" ")
        _beginDay = _beginTimeStrList[0]
        _beginTime = _beginTimeStrList[1]
        _endTimeStrList = _end.split(" ")
        _endDay = _endTimeStrList[0]
        _endTime = _endTimeStrList[1]
        print("当前获取数据的时间段为 : " + _begin + " -> " + _end)

        # # 请求记录
        _list = requestMeiQiaList(
            _beginDay,
            _beginTime,
            _endDay,
            _endTime,
            _templeteJsonStr,
            _which
        )

        _finallList = _finallList + _list
        # 数据长度判断，是否当前的记录已经结束
        while len(_list) == 20:
            print(" 获取进行中...")
            # 最后一条做起始时间，继续进行 "2018-12-08 06:11:26.514519"
            if _which == "tickets":
                _endTimeStr = _list[-1]["ticket_create_tm"]
            elif _which == "conversations":
                _endTimeStr = _list[-1]["conv_end_tm"]
            # 截取这个最后一条的时间点，从这个时间点继续查找，当然，这个时间点肯定会查找到自己的，要根据id去掉重
            _beginTimeResult = re.search(r'([0-9]*-[0-9]*-[0-9]*)\s([0-9]*\:[0-9]*\:[0-9]*)\.[0-9]*', _endTimeStr)
            # 查找后面的
            _list = requestMeiQiaList(
                _beginTimeResult.group(1),
                _beginTimeResult.group(2),
                _endDay,
                _endTime,
                _templeteJsonStr,
                _which
            )
            _finallList = _finallList + _list

        #
        _finallListRemoveSame = []
        _finallListRemoveSameDict = {}
        _conv_id_set = set()
        _conv_end_tm_set = set()

        _current_unique_id = ""

        if _which == "tickets":
            _current_unique_id = "ticket_id"
        elif _which == "conversations":
            _current_unique_id = "conv_id"

        for _conv in _finallList:
            if not _conv[_current_unique_id] in _conv_id_set:
                _conv_id_set.add(_conv[_current_unique_id])
                _finallListRemoveSame.append(_conv)
                _finallListRemoveSameDict[_conv[_current_unique_id]] = _conv
            else:
                _conv_already_save = _finallListRemoveSameDict[_conv[_current_unique_id]]
                _conv_str = str(json.dumps(_conv))
                _conv_already_save_str = str(json.dumps(_conv_already_save))
                if not _conv_str == _conv_already_save_str:
                    print("ERROR : 同一个 conv_id 内容不同")
        print("工获取到 : " + str(len(_finallListRemoveSame)) + " 条数据")

        print("正在整理数据格式")
        _outputStr = ""
        for _convDict in _finallListRemoveSame:
            _outputStr = _outputStr + str(json.dumps(_convDict)) + "\n"
        # 去掉最后一个多余的换行符
        _outputStr = _outputStr[:-1]
        # 文件没路径拼接
        _endHour = _endTime.split(":")[0]
        _beginHour = _beginTime.split(":")[0]
        # 零点的时候，会向后移一天，也就是说今夜的24点，会是明天的00点。所以，日期要减一天
        if _endHour == "00":
            _tempDatetime = strToDatetime(_endDay + " 12:00:00")
            _tempDatetimeYestoday = getDayFromTargetDay(_tempDatetime, -1)
            _tempDay = _tempDatetimeYestoday.split(" ")[0]
            _fileSubPath = _tempDay + "/" + _beginTime.split(":")[0] + "_" + _endTime.split(":")[0]
        else:
            _fileSubPath = _endDay + "/" + _beginTime.split(":")[0] + "_" + _endTime.split(":")[0]

        _filePath = _tempFilePath + "/" + _which + "/" + _fileSubPath
        print("正在写入临时文件 : " + _filePath)
        # 写入文件
        writeFileWithStr(
            _filePath,
            _outputStr.encode('UTF-8','ignore').decode('UTF-8')
        )
    # 生成的文件列表
    _filePathList = getFilterFilesInPath(_tempFilePath + "/" + _which + "/")

    print("正在建立 HDFS 客户端")
    # 链接hdfs 将临时文件拷贝到 目标路径，那个用户执行这个脚本，就是哪个用户
    _client = getClient(_hdfsUrl, None)
    for _filePath in _filePathList:
        _fileSubPath = _filePath.split(_tempFilePath)[1]
        _hdfsTargetFilePath = _hdfsTargetFolder + _fileSubPath
        print("正在将临时文件拷贝到 hdfs 中 : " + _hdfsTargetFilePath)
        # 覆盖掉原有的文件 overwrite
        _client.copy_from_local(_filePath, _hdfsTargetFilePath, overwrite=True)

    print("正在删除临时文件 : " + _tempFilePath + "/" + _which + "/")
    # 删除临时文件
    shutil.rmtree(_tempFilePath + "/" + _which + "/")
