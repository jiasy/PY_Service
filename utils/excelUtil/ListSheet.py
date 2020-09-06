# !/usr/bin/env python3
import utils
from utils.excelUtil.Sheet import Sheet


class ListSheet(Sheet):

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
                for _col in range(1, self.maxCol):
                    _parameterNames.append(utils.excelUtils.isParNameLegal(self.getStrByCr(_col, 1)))
                for _row in range(2, self.maxRow):
                    _dataObject = {}  # 创建数据对象
                    for _col in range(1, self.maxCol):
                        _dataObject[_parameterNames[_col - 1]] = self.getStrByCr(_col, _row)  # 识别一行数据,按照第二行的字段名进行写入
                    _list.append(_dataObject)  # 将数据添加到列表
                return _list
            else:
                raise TypeError("ERROR 作为 list 结构的Excel数据源，a2 内的字符串必须是 \"字段名\"")
                return None
        else:
            raise TypeError("ERROR 作为 list 结构的Excel数据源，a1 内的字符串必须是 \"中文名\"")
            return None
