# !/usr/bin/env python3
# 常见的属性列表。一般是技能，道具，等等的配置
from utils.excelUtil.Sheet import Sheet
from utils.excelUtil.Sheet import SheetType
from utils import convertUtils
from utils import excelUtils


class DictListSheet(Sheet):

    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.DICTLIST

    def toJsonDict(self):
        # sheet 是一个列表.
        # "a1"中文名 中文名称 [0,0],[1,0]~[maxCol,0] 开始就是 中文名
        # "a2"字段名 英文名称 [0,1],[1,1]~[maxCol,1] 开始就是 英文名
        # "a3"序号 数据起始  [0,2] ,[1,2]~[maxCol,2] 开始就是提第一条数据的每一项
        # 依次类推       [1,maxRow]~[maxCol,maxRow] 就是数据的最后一项
        if self.getStrByPos("a1") == "中文名":
            if self.getStrByPos("a2") == "字段名":
                _list = []
                _parameterNames = []  # 先获取字段名称
                for _col in range(1, self.maxCol):  # 数组中的字典对象，其中的属性可以不用判断前缀，因为没有类型判断需求
                    _parameterNames.append(excelUtils.isParNameLegal(self.getStrByCr(_col, 1)))
                for _row in range(2, self.maxRow):
                    _dataObject = {}  # 创建数据对象
                    for _col in range(1, self.maxCol):  # 参数所在位，填入对应的内容
                        _key = _parameterNames[_col - 1][3:]
                        _type = _parameterNames[_col - 1][0:3]
                        _cellStr = self.getStrByCr(_col, _row)
                        _value = None
                        if _type == "<i>":
                            _value = convertUtils.strToInt(_cellStr)
                        elif _type == "<f>":
                            _value = convertUtils.strToFloat(_cellStr)
                        elif _type == "<b>":
                            if _cellStr == 1.0 or _cellStr.lower() == "t" or \
                                    _cellStr.lower() == "true" or \
                                    _cellStr == "1" or _cellStr == "1.0":
                                _value = True
                            elif _cellStr == 0.0 or \
                                    _cellStr.lower() == "f" or \
                                    _cellStr.lower() == "false" or \
                                    _cellStr == "0" or _cellStr == "0.0":
                                _value = True
                            else:
                                print('_cellStr = ' + str(_cellStr))
                        elif _type == "<t>":
                            _value = convertUtils.strToInt(_cellStr)
                        elif _type == "<s>":
                            _value = _cellStr
                        _dataObject[_key] = _value  # 识别一行数据,按照第二行的字段名进行写入
                    _list.append(_dataObject)  # 将数据添加到列表
                return _list
            else:
                raise Exception("ERROR 作为 list 结构的Excel数据源，a2 内的字符串必须是 \"字段名\"")
                return None
        else:
            raise Exception("ERROR 作为 list 结构的Excel数据源，a1 内的字符串必须是 \"中文名\"")
            return None
