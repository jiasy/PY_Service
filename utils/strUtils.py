# !/usr/bin/env python3
import re

# 移除掉一些麻烦的字符串
chars = {
    '\xc2\x82': ',',  # High code comma
    '\xc2\x84': ',,',  # High code double comma
    '\xc2\x85': '...',  # Tripple dot
    '\xc2\x88': '^',  # High carat
    '\xc2\x91': '\x27',  # Forward single quote
    '\xc2\x92': '\x27',  # Reverse single quote
    '\xc2\x93': '\x22',  # Forward double quote
    '\xc2\x94': '\x22',  # Reverse double quote
    '\xc2\x95': ' ',
    '\xc2\x96': '-',  # High hyphen
    '\xc2\x97': '--',  # Double hyphen
    '\xc2\x99': ' ',
    '\xc2\xa0': ' ',
    '\xc2\xa6': '|',  # Split vertical bar
    '\xc2\xab': '<<',  # Double less than
    '\xc2\xbb': '>>',  # Double greater than
    '\xc2\xbc': '1/4',  # one quarter
    '\xc2\xbd': '1/2',  # one half
    '\xc2\xbe': '3/4',  # three quarters
    '\xca\xbf': '\x27',  # c-single quote
    '\xcc\xa8': '',  # modifier - under curve
    '\xcc\xb1': ''  # modifier - under line
}


# 匹配到的为 key，这里得到的就是返回 value
def replace_chars(match):
    return chars[match.group(0)]


# 替换字符串
# str_ 中的 sourceStr_ 替换成 targetStr_
def replaceStr(str_: str, sourceStr_: str, targetStr_: str):
    str_ = str_.replace(sourceStr_, targetStr_)
    return str_


# 把 chars 中的字符串做 key，替换成对应 value
def removeAnnoyingChars(targetStr_):
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, targetStr_)


# 首字母小写
def lowerFirstChar(str_):
    return str_[0].lower() + str_[1:]


# 判断字符串是否是数字
def is_number(str_):
    try:
        float(str_)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(str_)
        return True
    except (TypeError, ValueError):
        pass

    return False


# # match 就是识别字符串是否以表达式开头
# # 以 . 开头的字符串
# re.match(r'\..*')
# # 以 双下岗线开头的字符串
# re.match(r'__.*')
# # 以 任意字符串 开头，.pyc结尾的字符串
# re.match(r'.*\.pyc')
# # 完整文件名
# re.match(r'metastore_db')
#
# _reStrList = [
#     '\..*',
#     '__.*',
#     '.*\.pyc',
#     'metastore_db'
# ]
# strUtils.isStrInFilterList(_reStrList,".git")

def isStrInFilterList(filterList_, str_):
    for _rStr in filterList_:
        if re.match(_rStr, str_):
            return True
    return False


# 多个连续空格变成一个空格,去两边空格
def spacesReplaceToSpace(str_):
    return re.sub(' +', ' ', str_).lstrip().rstrip()


# 多行矩阵字符串 转换成 矩阵。每一个行为第二维度，每一行内的通过分割符的构成第一维
def strToMatrix(str_: str, splitStr_: str = ","):
    _lines = str_.split("\n")
    _matrix = []
    for _line in _lines:
        if not _line == "":
            _matrix.append(_line.split(splitStr_))
    return _matrix


# str_ 中 出现多少次 char_
def charCount(str_: str, char_: str):
    return list(str_).count(char_)


# 版本号比较
# _compareInt = strUtils.versionCompare("1.1.2", "1.1.3")
# if (_compareInt == 1):  # 1大2小
#
# elif (_compareInt == -1):  # 2大1小
#
# elif (_compareInt == 0):  # 相同
#
# elif:  # 版本号出错
def versionCompare(v1: str = "1.1.1", v2: str = "1.2"):
    if not isVersionStr(v1) or not isVersionStr(v2):
        return None
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    v1_len = len(v1_list)
    v2_len = len(v2_list)
    if v1_len > v2_len:
        for i in range(v1_len - v2_len):
            v2_list.append("0")
    elif v2_len > v1_len:
        for i in range(v2_len - v1_len):
            v1_list.append("0")
    else:
        pass
    for i in range(len(v1_list)):
        if int(v1_list[i]) > int(v2_list[i]):
            # v1大
            return 1
        if int(v1_list[i]) < int(v2_list[i]):
            # v2大
            return -1
    # 相等
    return 0


# 检测当前名称是否是版本号
def isVersionStr(ver_: str):
    _verCheck = re.match("\d+(\.\d+){0,2}", ver_)
    if _verCheck is None or _verCheck.group() != ver_:
        return False
    else:
        return True


# 检查当前行，从指定位开始，是不是想要的字符串，并且，返回找到后，刨去字符串的新位置
def checkStr(line_: str, idx_: int, checkStr_: str):
    _commentLiength = len(checkStr_)
    if idx_ + _commentLiength <= len(line_):
        if line_[idx_:idx_ + _commentLiength] == checkStr_:
            return (True, idx_ + _commentLiength)
    return (False, idx_)

# 模板里面的键，替换成给定字典中的对应键的值
def replaceKeyToValueInTemplate(replaceDict_: dict, templateStr_: str):
    return templateStr_.format(**replaceDict_)
