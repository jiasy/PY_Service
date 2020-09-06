# !/usr/bin/env python3
# excel解析工具
import re
from utils import dictUtils
from utils.excelUtil import WorkBook
import json

# 列名 数字 对应 关系
colNameList = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj", "ak", "al", "am",
    "an", "ao", "ap", "aq", "ar", "as", "at", "au", "av", "aw", "ax", "ay", "az",
    "ba", "bb", "bc", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bk", "bl", "bm",
    "bn", "bo", "bp", "bq", "br", "bs", "bt", "bu", "bv", "bw", "bx", "by", "bz",
    "ca", "cb", "cc", "cd", "ce", "cf", "cg", "ch", "ci", "cj", "ck", "cl", "cm",
    "cn", "co", "cp", "cq", "cr", "cs", "ct", "cu", "cv", "cw", "cx", "cy", "cz",
    "da", "db", "dc", "dd", "de", "df", "dg", "dh", "di", "dj", "dk", "dl", "dm",
    "dn", "do", "dp", "dq", "dr", "ds", "dt", "du", "dv", "dw", "dx", "dy", "dz",
    "ea", "eb", "ec", "ed", "ee", "ef", "eg", "eh", "ei", "ej", "ek", "el", "em",
    "en", "eo", "ep", "eq", "er", "es", "et", "eu", "ev", "ew", "ex", "ey", "ez",
]


# 列行 转换 格子 字符串
def crToPos(col_, row_):
    return str(colNameList[col_] + str(int(row_ + 1)))


# 列行 转换 格子 字符串
def cToPos(col_):
    return str(colNameList[col_])


# 格子 字符串 转换 列行
def posToCr(posStr_):
    _posStrMatch = re.search(r'([a-z]*)(\d+)', posStr_)
    if _posStrMatch:
        _colName = str(_posStrMatch.group(1))
        _rowNum = int(_posStrMatch.group(2))
        _colNum = colNameList.index(str(_colName).lower())
        _rowNum -= 1
        return _colNum, _rowNum
    else:
        raise TypeError("Sheet.getStrByPos posStr_ : " + posStr_ + " 参数不正确")


# 字段命名规范 -----------------------------------------------------------------------------------------------------------
# 判断一个参数的命名是否符合命名规范.
def isParNameLegal(parameterName_):
    if not isParNameData(parameterName_) and not isParNameStructure(parameterName_):
        raise TypeError('字段名称必须是t,s,u,i,f,b,d,l中的一个,当前字段名为 : ' + parameterName_)
    else:
        return parameterName_


# 属性名是一个数据， t 时间 , s 字符串 , u 唯一确定 , i 整形 , f 浮点 , b 布尔
def isParNameData(parameterName_):
    if (parameterName_.startswith("t") or parameterName_.startswith("s") or parameterName_.startswith(
            "u") or parameterName_.startswith("i") or parameterName_.startswith("f") or parameterName_.startswith("b")):
        return True
    else:
        return False


# 属性名是一个结构，d 字典 , l 列表
def isParNameStructure(parameterName_):
    if parameterName_.startswith("d") or parameterName_.startswith("l"):
        return True
    else:
        return False


# sheet页面规范，分以下几种。识别到固定的命名，做固定的操作。
#   列表类【list】，每一行是一条数据
#       将页面变成列表。list_ 开头的sheet页名称。
#           第一行，中文名称
#           第二行，英文Key值
#           第三行，数据
#   字典类【dict】，有层级结构，类似JSON
#       将页面内容变成json结构，dict_ 开头的sheet页名称。
#           连续有值的行为数据。直到出现第一个空行
#   键值类【kv】
#       将页面内容变成只有一层的键值结构字典。kv_ 开头的sheet页名称。
#           只第一列没有第二列，注释
#           第一列，键名 第二列，值
#           直到出现第一个空行
#   Proto类【proto】(ktv)
#       页面中有多个键值结构，同一个功能集中在同一个Excel中。proto_ 开头的sheet页名称。
#           第一列，结构名
#               第二列，键名 第三列，类型 第四列，值
#           直到出现第一个空行，或者，第一列出现新结构
#   交叉类【relation】，横竖交叉点表示是否有关联
#       将页面内容变成一个关系图，横竖项通过交叉点是否添值关联。relation_ 开头的sheet页名称。
#           第一列，中文描述。第一行中文描述
#   状态机【state】，
#       行列必须一一对应，交叉点表示从行到列的推进驱动字符。state_ 开头的sheet页名称。
#           第一行，中文描述。第一列的竖向和第二行的横向，逐一匹配一致。
#               节点解析成 from trans to 的格式，from通过trans到to的意思。
#   工作流【cmd】，通过固定格式的配置 PY_Service 运行
#       单独运行，或者在Jenkins下运行。cmd_ 开头的sheet页名称。
if __name__ == "__main__":
    _currentWorkBook = WorkBook.WorkBook()
    _currentWorkBook.initWithWorkBook("/Users/jiasy/Desktop/dataBase.xlsx")
    _excelDict = {}
    for _sheetName in _currentWorkBook.sheetDict:
        _sheet = _currentWorkBook.sheetDict[_sheetName]
        _key = _sheetName.split("_")[1]
        _value = _sheet.toJsonDict()
        print(_sheetName + " -----------------------------------------------")
        dictUtils.showDictStructure(_value)
        _excelDict[_key] = _value
    print(" -----------------------------------------------")
    print(json.dumps(_excelDict, indent=4, sort_keys=False, ensure_ascii=False))
