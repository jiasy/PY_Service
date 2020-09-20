# !/usr/bin/env python3
# json结构的复杂列表。
# 将Excel转换成字典，这里需要有类型指定。因为列表中有各种类型的对象混排时，类型判断会变得十分复杂。
# 通过前缀来判断类型。属性名大写。
import utils
from utils.excelUtil.Sheet import Sheet
from utils.excelUtil.Sheet import SheetType


class DictSheet(Sheet):
    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.DICT

    def toJsonDict(self):
        return self.getDict(0, self.maxCol, 0, self.maxRow)

    def keyWithOutType(self, parName_: str):
        return parName_.split(">").pop()

    def getDict(self, colStartIdx_: int, colEndID_: int, rowStartIdx_: int, rowEndID_: int):
        # self是一个字典
        # 靠缩进来进行json的属性归属
        # 数据的字段名必须进行类型指定,这样方面识别
        # 从上向下,进行一次路径识别,确保字典和列表的字段名站整个一行
        for _currentRow in range(rowStartIdx_, rowEndID_):  # 一行一行向下找
            for _currentCol in range(colStartIdx_, colEndID_):  # 每一行，要么是个结构，要么是列表，要么是一个数据
                if not self.getCellStructureData(  # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
                        _currentCol, _currentRow
                ) is None:
                    break  # 得到了,这一行就结束了
                elif not utils.excelUtils.getCellParData(  # 是数据项,那它右面的第一项就是数据,<再往右面就全都是空>
                        self, _currentCol, _currentRow
                ) is None:
                    break  # 得到了,这一行就结束了

        _dictData = {}  # 开始组装
        for _currentRow in range(rowStartIdx_, rowEndID_):
            _cell = self.cells[colStartIdx_][_currentRow]
            if self.cells[colStartIdx_][_currentRow].strValue:
                if hasattr(_cell, "data") and _cell.data:
                    if _cell.data["type"] == "<d>":  # 字典
                        _dictData[_cell.data["parName"]] = dict(self.structDict(_cell))
                    elif _cell.data["type"] == "<l>":  # 列表
                        _dictData[_cell.data["parName"]] = list(self.structList(_cell))
                    else:
                        _dictData[_cell.data["parName"]] = _cell.data["value"]
        return _dictData

    # 构建字典
    def structDict(self, cell_):
        _dictData = {}
        for _cell in cell_.data["cellList"]:
            if hasattr(_cell, "data") and _cell.data:
                if _cell.data["type"] == "<d>":  # 字典
                    _dictData[_cell.data["parName"]] = dict(self.structDict(_cell))
                elif _cell.data["type"] == "<l>":  # 列表
                    _dictData[_cell.data["parName"]] = list(self.structList(_cell))
                else:
                    _dictData[_cell.data["parName"]] = _cell.data["value"]
        return _dictData

    # 构建列表
    def structList(self, cell_):
        _listData = []
        for _cell in cell_.data["cellList"]:
            if hasattr(_cell, "data") and _cell.data:
                if _cell.data["type"] == "<d>":  # 字典
                    _listData.append(dict(self.structDict(_cell)))
                elif _cell.data["type"] == "<l>":  # 列表
                    _listData.append(list(self.structList(_cell)))
                else:
                    _listData.append(_cell.data["value"])
        return _listData

    def getCellStructureData(self, col_, row_):  # cell里面是一个结构名,获取它所持有的数据
        _dataInfo = None
        _cellStr = self.getStrByCr(col_, row_)
        if utils.excelUtils.isParNameStructure(_cellStr):  # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
            _cell = self.cells[col_][row_]  # 获取格子
            _dataInfo = {"parName": _cellStr[3:], "type": _cellStr[0:3], "cellList": []}  # 获取它的结构 格子中写入数据
            # 先存cell,然后按照类型组装成dict/list.遍历过程只负责关联,并不组装
            _rangeRow = row_  # 向下找,找到下一个数据/结构,确定它将持有多少行
            for _currentValueCol in range(col_ + 1):  # 它的左下方任意一个格子有值都是它的数据的结构截止点
                if row_ < self.maxRow:
                    for _currentValueRow in range(row_ + 1, self.maxRow):
                        if self.getStrByCr(_currentValueCol, _currentValueRow) != "":
                            _rangeRow = _currentValueRow
                            break

            if _rangeRow == row_:  # 等同于初始.证明找到底了都没找到.那就是到底为范围
                _rangeRow = self.maxRow

            if row_ < self.maxRow:
                for _currentValueRow in range(row_ + 1, _rangeRow):  # 关联的子属性,从下一列开始,因为它自己就是结构了,所以它关联的都是他的属性
                    if self.getStrByCr(col_ + 1, _currentValueRow) != "":
                        _dataInfo["cellList"].append(self.cells[col_ + 1][_currentValueRow])
            _cell.data = _dataInfo
            for _currentValueCol in range(col_ + 1, self.maxCol):  # 当前行向后找
                if not (self.getStrByCr(_currentValueCol, row_) == ""):  # 如果出现不为空的格子,报错
                    self.raiseAndPrintError(
                        utils.excelUtils.crToPos(
                            _currentValueCol, row_
                        ) + " 不能有值,因为 " + utils.excelUtils.crToPos(
                            col_, row_
                        ) + " 是一个列表命名/字典命名")
            # print('_dataInfo : ' + str(_dataInfo))
        return _dataInfo
