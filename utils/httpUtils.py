# !/usr/bin/env python3

import sys
import json
import requests
import re
import datetime
import utils.fileUtils
import utils.timeUtils
from urllib import parse, request
from urllib.error import HTTPError, URLError


# json对象的键值对展开，形成参数，访问网址提供的API
def requestApi(url_: str):
    r = requests.get(url_)
    if r.status_code == 200:
        response_dict = r.json()  # API返回json格式的信息（将响应存储到变量中）
        # print('response_dict = ' + str(str(json.dumps(response_dict, indent=4, sort_keys=False, ensure_ascii=False))))
        return response_dict
    else:
        print("HttpUtils requestApi status code :", r.status_code)  # 判断请求是否成功（状态码200时表示请求成功）
        return None


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


def read_whole_data(url):
    the_page = ''
    values = {'userid': 'userid', 'pwd': 'pwd'}
    data = parse.urlencode(values).encode(encoding='UTF8')
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent, 'Referer': 'http://www.python.org/'}
    req = request.Request(url, data, headers)

    try:
        response = request.urlopen(req, timeout=10)
    except HTTPError as e:
        print('Error code: %s', e.code)
    except URLError as e:
        print('Error reason: %s', e.reason)
    else:
        the_page = response.read().decode("utf8")

    return the_page


def filterData(sourcedata):
    regEx = r'alt="(.*)"/><span>(.*)</span></a>[\s\S]+?<a href="(.*.html)"[\s\S]+?<h3>(.*)</h3><p[^>]*>([^<]*)[\s\S^h]*?</?span.*?></p><p[^>]*><span[^>]*>(.*)</span>(.*)</p></a></li>'
    rules = re.compile(regEx)
    result = rules.findall(sourcedata)
    return result


if __name__ == "__main__":
    _templeteJsonStr = \
        """
    {{
      "conv_start_from_tm": "{beginDay}+{beginTime}",
      "conv_start_to_tm": "{endDay}+{endTime}",
      "offset": 0,
      "limit": 20,
      "app_id": "appId",
      "sign": "signToken",
      "enterprise_id": "53824"
    }}
        """


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

    '''
    美洽的api,支持12小时以内的查询，且每次只返回20个消息
    请求回来的数据格式
    +--result [0]
    |      +--enterprise_id
    |      +--dev_client_id
    |      +--page_from_url
    |      +--page_land_url
    |      +--page_land_title
    |      +--page_conv_url
    |      +--page_conv_title
    |      +--search_engine_name
    |      +--search_engine_kw
    |      +--visitor_ip
    |      +--visitor_location
    |      +--visitor_os
    |      +--visitor_browser
    |      +--visitor_tags [0]
    |      |      - <str>
    |      +--client_id
    |      +--client_info
    |      |      +--_m_track_id
    |      |      +--visitor_name
    |      +--agent_account
    |      +--agent_name
    |      +--agent_ID
    |      +--conv_id
    |      +--conv_start_tm
    |      +--conv_end_tm
    |      +--conv_first_resp_wait_in_secs
    |      +--conv_content [0]
    |      |      +--from
    |      |      +--timestamp
    |      |      +--content
    |      |      +--type
    |      +--conv_agent_msg_count
    |      +--conv_visitor_msg_count
    |      +--conv_quality_grade
    |      +--conv_leads
    |      +--comment_level
    |      +--comment_content
    +--errno
    +--errmsg
    '''
    # 最终结果数组
    _finallList = []

    # 起止时间
    _beginDay = "2019-02-14"
    _beginTime = "00:00:00"
    _endDay = "2019-02-20"
    _endTime = "00:00:00"
    # 转换起止时间
    _begindDateTime = utils.timeUtils.strToDatetime(_beginDay + " " + _beginTime)
    _endDateTime = utils.timeUtils.strToDatetime(_endDay + " " + _endTime)
    # 半天为间隔分割是时间段
    _timeList = utils.timeUtils.devideTwoDatetimeIntoList(_begindDateTime, _endDateTime, datetime.timedelta(days=0.5))
    _timeStrList = [utils.timeUtils.datetimeToStr(_time) for _time in _timeList]
    # 最后一项时间小于截止时间的时候，把截止时间添加到最后
    if utils.timeUtils.datetimeToStr(_endDateTime) > _timeStrList[-1]:
        _timeStrList.append(utils.timeUtils.datetimeToStr(_endDateTime))
    print('_timeStrList = ' + str(_timeStrList))

    for _i in range(len(_timeStrList) - 1):
        # 前一项做为起始时间，后一项作为结束时间，进行数据获取
        _begin = _timeStrList[_i]
        _end = _timeStrList[_i + 1]
        _beginTimeStrList = _begin.split(" ")
        _beginDay = _beginTimeStrList[0]
        _beginTime = _beginTimeStrList[1]
        _endTimeStrList = _end.split(" ")
        _endDay = _endTimeStrList[0]
        _endTime = _endTimeStrList[1]
        print("current : " + _begin + " -> " + _end)

        # # 请求记录
        _list = requestMeiQiaList(
            _beginDay,
            _beginTime,
            _endDay,
            _endTime,
            _templeteJsonStr
        )
        _finallList = _finallList + _list
        print("     add : " + str(len(_list)))

        # 数据长度判断，是否当前的记录已经结束
        while len(_list) == 20:
            # 最后一条做起始时间，继续进行 "2018-12-08 06:11:26.514519"
            _endTimeStr = _list[-1]["conv_end_tm"]
            # 截取这个最后一条的时间点，从这个时间点继续查找，当然，这个时间点肯定会查找到自己的，要根据id去掉重
            _beginTimeResult = re.search(r'([0-9]*-[0-9]*-[0-9]*)\s([0-9]*\:[0-9]*\:[0-9]*)\.[0-9]*', _endTimeStr)
            # 查找后面的
            _list = requestMeiQiaList(
                _beginTimeResult.group(1),
                _beginTimeResult.group(2),
                _endDay,
                _endTime,
                _templeteJsonStr
            )
            _finallList = _finallList + _list
            print("     add : " + str(len(_list)))
        print(" count : " + str(len(_finallList)))

    _finallListRemoveSame = []
    _conv_id_set = set()
    _conv_end_tm_set = set()
    for _conv in _finallList:
        if not _conv["conv_id"] in _conv_id_set:
            _conv_id_set.add(_conv["conv_id"])
            _finallListRemoveSame.append(_conv)

    print('len(_finallListRemoveSame) = ' + str(len(_finallListRemoveSame)))

    utils.fileUtils.writeFileWithStr(
        '/Users/jiasy/Desktop/MeiQia',
        str(
            json.dumps(
                _finallListRemoveSame,
                indent=4,
                sort_keys=False,
                ensure_ascii=False
            )
        )
    )
