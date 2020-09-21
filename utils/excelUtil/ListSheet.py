# !/usr/bin/env python3
# 常见的属性列表。一般是技能，道具，等等的配置
from utils.excelUtil.DictListSheet import DictListSheet
from utils.excelUtil.Sheet import SheetType
import sys


class ListSheet(DictListSheet):

    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.LIST

    def toJsonDict(self):
        _dictList = super().toJsonDict()
        _list = []
        _parameterNameList = []
        if len(_dictList) > 0:  # 获取参数名列表
            _dict = _dictList[0]
            for _key in _dict:
                _parameterNameList.append(_key)
        else:
            print(self.sheetName + " : 数据为空")
            sys.exit(1)
        _list.append(_parameterNameList)  # 第一行是属性名称
        for _i in range(len(_dictList)):
            _dict = _dictList[_i]
            _dictValueList = []
            for _j in range(len(_parameterNameList)):  # 按照参数排列的顺序
                _parameterName = _parameterNameList[_j]  # 获取参数的值
                _dictValueList.append(_dict[_parameterName])  # 同参数顺序，写入第二维数组中
            _list.append(_dictValueList)  # 构成二维数组
        return _list
