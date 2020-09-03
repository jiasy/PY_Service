# !/usr/bin/env python3
import datetime
import re
import time
import utils.pyUtils
import utils.listUtils

'''
first_date = datetime.strptime('2014-7-1', '%Y-%m-%d')
%A 星期的名称，如Monday
%B 月份名，如January
%m 用数字表示的月份（01~12）
%d 用数字表示月份中的一天（01~31）
%Y 四位的年份，如2015
%y 两位的年份，如15
%H 24小时制的小时数（00~23）
%I 12小时制的小时数（01~12）
%p am或pm
%M 分钟数（00~59）
%S 秒数（00~61）
'''


# ------------------------------------时间戳---------------------------------------------------------------------------------------
def time_stamp():
    # datetime.now() = 2018-12-21 17:18:38.724660
    _reg = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)\.(\d+)', str(datetime.datetime.now()))
    if _reg:
        return str(_reg.group(2)) + "_" + str(_reg.group(3)) + "_" + str(_reg.group(4)) + "_" + str(_reg.group(5))
    else:
        print("ERROR : 时间戳格式错误 ")


def today_Y_M_D():
    _today = datetime.datetime.now()
    return _today.strftime("%Y-%m-%d")


def now():
    print("datetime.now() = " + str(datetime.datetime.now()))
    return


# 今天为基准，偏移几天，得到日期
def getDayFromToday(bufferDay_: int):
    _today = datetime.date.today()
    _realDay = _today + datetime.timedelta(days=bufferDay_)
    return _realDay.strftime("%Y-%m-%d")


# 以某一天为基准
def getDayFromTargetDay(targetDateTime_, bufferDay_: int):
    _realDay = targetDateTime_ + datetime.timedelta(days=bufferDay_)
    return _realDay.strftime("%Y-%m-%d %H:%M:%S")


# 字符串转换成时间
def strToDatetime(str_: str, format_: str = None):
    _format = "%Y-%m-%d %H:%M:%S"
    if format_:
        _format = format_
    _timeArray = time.strptime(str_, _format)
    return datetime.datetime(*_timeArray[0:6])


# 字符串转换成时间戳
def strToTimestamp(str_):
    _timeArray = strToTimeArray(str_)
    _timeStamp = int(time.mktime(_timeArray))
    return _timeStamp


# 字符串转换成时间数组
def strToTimeArray(str_: str):
    _timeArray = time.strptime(str_, "%Y-%m-%d %H:%M:%S")
    return _timeArray


def timestampToDatetime(ts_):
    return datetime.datetime.fromtimestamp(ts_)


def datetimeToTimestamp(datetime_):
    return datetime_.timestamp()


# 时间转换成字符串
def datetimeToStr(datetime_, format_: str = None):
    _format = "%Y-%m-%d %H:%M:%S"
    if format_:
        _format = format_
    return datetime_.strftime(_format)


# 当前时间戳
def nowTimeStamp():
    return int(time.time())


# 比较两个时间大小
def compareDatetime(datetime1_, datetime2_):
    return compareTimeStr(datetimeToStr(datetime1_), datetimeToStr(datetime2_))


# 比较字符串时间大小
def compareTimeStr(timeStr1_, timeStr2_):
    _reg1 = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', timeStr1_)
    _reg2 = re.search(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', timeStr2_)
    if _reg1 and _reg2:
        return timeStr1_ > timeStr2_
    else:
        raise utils.pyUtils.AppError("字符串需要符合固定格式才能进行比较 %Y-%m-%d %H:%M:%S \n" + timeStr1_ + '\n' + timeStr2_)
        return None


# 等分两个时间点
# datetimeTimedelta_ : datetime.timedelta(days=1)/datetime.timedelta(seconds=1)..
def devideTwoDatetimeIntoList(datetime1_, datetime2_, datetimeTimedelta_):
    _datetimeList = [datetime1_, datetime1_ + datetimeTimedelta_]
    # 如果 最后一项 + 时间间隔 没能超过 最后时间，就再向数组内添加一个时间
    # 直到超过了截止时间
    while not compareDatetime(_datetimeList[len(_datetimeList) - 1], datetime2_):
        _datetimeList.append(_datetimeList[-1] + datetimeTimedelta_)
    # 因为最后一项超过了截止时间，不在时间段内，所以要移除最后一项
    utils.listUtils.list_pop(_datetimeList)
    return _datetimeList


# 获取一天的24个小时
def get24TimeStrInOneDay(dataStr_: str):
    _timeStrList = []
    # 补一个正当午的时分秒，然后取得时间
    _datetime = strToDatetime(dataStr_ + " 12:00:00")
    for x in range(24):
        _timeStr = _datetime.strftime("%Y-%m-%d") + " %2d:00:00" % x
        _timeStrList.append(_timeStr)
    return _timeStrList


# 获得两天之间所有天的字符串
def getDaysBetween(beginDay_: str, endDay_: str):
    _dayStrList = []
    _datetimeList = devideTwoDatetimeIntoList(
        strToDatetime(beginDay_ + " 00:00:00"),
        strToDatetime(endDay_ + " 00:00:00"),
        datetime.timedelta(days=1)
    )
    print('_datetimeList = ' + str(_datetimeList))
    for _i in range(len(_datetimeList)):
        _datetime = _datetimeList[_i]
        _dayStrList.append(datetimeToStr(_datetime, "%Y-%m-%d"))
    return _dayStrList


if __name__ == "__main__":
    _dayStrList = getDaysBetween("2019-1-1", "2019-2-1")
    for _i in range(len(_dayStrList)):
        _dayStr = _dayStrList[_i]
        print(_dayStr)

    _hourList = get24TimeStrInOneDay("2019-1-1")
    for _i in range(len(_hourList)):
        _hourStr = _hourList[_i]
        print(_hourStr)
