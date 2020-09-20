# !/usr/bin/env python3
# excel解析工具
import re
from utils import dictUtils
from utils import convertUtils
from utils.excelUtil import Sheet
from utils.excelUtil import WorkBook
import json
import os

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
        raise Exception("Sheet.getStrByPos posStr_ : " + posStr_ + " 参数不正确")


# 字段命名规范 -----------------------------------------------------------------------------------------------------------
# 判断一个参数的命名是否符合命名规范.
def isParNameLegal(parameterName_):
    if not isParNameData(parameterName_) and not isParNameStructure(parameterName_):
        raise Exception('字段名称必须是t,s,i,f,b,d,l中的一个,当前字段名为 : ' + parameterName_)
    else:
        return parameterName_


# 属性名是一个数据， t 时间 , s 字符串 ,i 整形 , f 浮点 , b 布尔
def isParNameData(parameterName_):
    if (
            parameterName_.startswith("<t>") or
            parameterName_.startswith("<s>") or
            parameterName_.startswith("<i>") or
            parameterName_.startswith("<f>") or
            parameterName_.startswith("<b>")
    ):
        return True
    else:
        return False


# 属性名是一个结构，d 字典 , l 列表
def isParNameStructure(parameterName_):
    if parameterName_.startswith("<d>") or parameterName_.startswith("<l>"):
        return True
    else:
        return False


# 设置键值对儿
def setKeyValue(dict_: dict, key_: str, sheet_, colNum_, rowNum_):
    _cellStr = sheet_.getStrByCr(colNum_, rowNum_)
    if isParNameData(key_):
        _value = None
        _type = key_[0:3]
        if _type == "<i>":
            _value = convertUtils.strToInt(_cellStr)
        elif _type == "<f>":
            _value = convertUtils.strToFloat(_cellStr)
        elif _type == "<b>":
            _cellValue = _cellStr
            if _cellValue == 1.0 or _cellValue.lower() == "t" or \
                    _cellValue.lower() == "true" or \
                    _cellValue == "1":
                _value = True
            elif _cellValue == 0.0 or \
                    _cellValue.lower() == "f" or \
                    _cellValue.lower() == "false" or \
                    _cellValue == "0":
                _value = True
            else:
                sheet_.raiseAndPrintError(
                    crToPos(colNum_, rowNum_) + " 所在为一个Boolean值,只能是1/0 true/false t/f 中的一个"
                )
        elif _type == "<t>" or _type == "<s>":
            _value = _cellStr
        dict_[key_[3:]] = _value
    else:
        dict_[key_] = sheet_.getStrByCr(colNum_, rowNum_)


# cell里面是一个数据名,那么取得它的数据信息并且返回
def getCellParData(sheet_: Sheet, col_, row_):
    _dataInfo = None
    _cellStr = sheet_.getStrByCr(col_, row_)
    if isParNameData(_cellStr):  # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
        _cell = sheet_.cells[col_][row_]  # 获取格子
        _dataInfo = {"parName": _cellStr[3:], "type": _cellStr[0:3]}  # 格子中写入数据
        _cellNextColStr = sheet_.getStrByCr(col_ + 1, row_)
        if _cellNextColStr == "" and not _dataInfo["type"] == "<s>":
            sheet_.raiseAndPrintError(
                crToPos(col_, row_) + "不为<s>键" + "，" +
                crToPos(col_ + 1, row_) + " 没有值，只有<s>才能有空字符串"
            )
        if not _cellNextColStr:
            sheet_.raiseAndPrintError(
                crToPos(col_, row_) + " " + _cellStr + " -> " +
                crToPos(col_ + 1, row_) + " 没有值"
            )
        if _dataInfo["type"] == "<i>":
            _dataInfo["value"] = convertUtils.strToInt(_cellNextColStr)
        elif _dataInfo["type"] == "<f>":
            _dataInfo["value"] = convertUtils.strToFloat(_cellNextColStr)
        elif _dataInfo["type"] == "<b>":
            _cellValue = _cellNextColStr
            if _cellValue == 1.0 or \
                    _cellValue.lower() == "t" or \
                    _cellValue.lower() == "true" or \
                    _cellValue == "1":
                _dataInfo["value"] = True
            elif _cellValue == 0.0 or \
                    _cellValue.lower() == "f" or \
                    _cellValue.lower() == "false" or \
                    _cellValue == "0":
                _dataInfo["value"] = True
            else:
                sheet_.raiseAndPrintError(
                    crToPos(col_, row_) + " 所在为一个Boolean值,只能是1/0 true/false t/f 中的一个"
                )
        elif _dataInfo["type"] == "<t>" or \
                _dataInfo["type"] == "<s>":
            _dataInfo["value"] = _cellNextColStr

        _cell.data = _dataInfo
        if int(col_ + 2) < sheet_.maxCol:  # <再往后都是空白><但是可能往后超过了列数限制-判断一下>
            for _currentValueCol in range(col_ + 2, sheet_.maxCol):  # 当前行向后找
                if not (sheet_.getStrByCr(_currentValueCol, row_) == ""):  # 如果出现不为空的格子,报错
                    sheet_.raiseAndPrintError(
                        crToPos(
                            _currentValueCol, row_
                        ) + " 不能有值,因为 " + crToPos(
                            col_, row_
                        ) + " 是一个数据")
        # print("data : " + str(_dataInfo))
    return _dataInfo


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
#       每一个Sheet是一个json文件。
#           每一列为一个类目
#       按类目形成一个独立的文件夹，放置每个sheet生成的json。
#   Proto类【proto】(ktv)
#       页面中有多个键值结构，同一个功能集中在同一个Excel中。proto_ 开头的sheet页名称。
#           第一列，结构名
#               第二列，键名 第三列，类型 第四列，值
#           直到出现第一个空行，或者，第一列出现新结构
#   状态机【state】，
#       行列必须一一对应，交叉点表示从行到列的推进驱动字符。state_ 开头的sheet页名称。
#           第一行，中文描述。第一列的竖向和第二行的横向，逐一匹配一致。
#               节点解析成 from trans to 的格式，from通过trans到to的意思。
#   工作流【cmd】，通过固定格式的配置 PY_Service 运行
#       单独运行，或者在Jenkins下运行。cmd_ 开头的sheet页名称。
if __name__ == "__main__":
    from utils.excelUtil.Sheet import SheetType

    # excel样例
    _parentPath = os.path.dirname(os.path.realpath(__file__))
    _excelUtilResPath = os.path.join(_parentPath, "excelUtil", "res")
    _excelPath = os.path.join(_excelUtilResPath, "dataBase.xlsx")
    # 解析样例
    _currentWorkBook = WorkBook.WorkBook()
    _currentWorkBook.initWithWorkBook(_excelPath)
    _excelDict = {}
    for _sheetName in _currentWorkBook.sheetDict:
        _sheet = _currentWorkBook.sheetDict[_sheetName]
        _value = _sheet.toJsonDict()
        _key = _sheetName
        print(_key + " -----------------------------------------------")
        dictUtils.showDictStructure(_value)
        _excelDict[_key] = _value
        if _sheet.sheetType == SheetType.STATE:  # 状态机，还要生成一下图片
            _sheet.toDotPng("/Users/jiasy/Downloads/")

    print(" -----------------------------------------------")
    print(json.dumps(_excelDict, indent=4, sort_keys=False, ensure_ascii=False))
