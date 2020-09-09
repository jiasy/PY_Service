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

    def getDict(self, colStartIdx_: int, colEndID_: int, rowStartIdx_: int, rowEndID_: int):
        # self是一个字典
        # 靠缩进来进行json的属性归属
        # 数据的字段名必须进行类型指定,这样方面识别
        # 从上向下,进行一次路径识别,确保字典和列表的字段名站整个一行
        for _currentRow in range(rowStartIdx_, rowEndID_):
            for _currentCol in range(colStartIdx_, colEndID_):
                if not self.getCellStructureData(_currentCol, _currentRow) is None:  # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
                    break  # 得到了,这一行就结束了
                elif not self.getCellParData(_currentCol, _currentRow) is None:  # 是数据项,那它右面的第一项就是数据,<再往右面就全都是空>
                    break  # 得到了,这一行就结束了

        _dictData = {}  # 开始组装
        for _currentRow in range(rowStartIdx_,rowEndID_):
            _cell = self.cells[colStartIdx_][_currentRow]
            if self.cells[colStartIdx_][_currentRow].strValue:
                if hasattr(_cell, 'data'):
                    _cellData = _cell.data
                    if utils.excelUtils.isParNameData(_cellData["parName"]):  # 如果当前是个数据
                        _dictData[_cellData["parName"]] = _cellData["value"]
                    elif utils.excelUtils.isParNameStructure(_cellData["parName"]):
                        if _cellData["type"] == "d":  # 字典
                            _dictData[_cellData["parName"]] = dict(self.structDict(_cell))
                        elif _cellData["type"] == "l":  # 列表
                            _dictData[_cellData["parName"]] = list(self.structList(_cell))
        return _dictData

    # 构建字典
    def structDict(self, cell_):
        _dictData = {}
        for _cell in cell_.data["cellList"]:
            if hasattr(_cell, 'data'):
                _cellData = _cell.data
                if utils.excelUtils.isParNameData(_cellData["parName"]):  # 如果当前是个数据
                    _dictData[_cellData["parName"]] = _cellData["value"]
                elif utils.excelUtils.isParNameStructure(_cellData["parName"]):
                    if _cellData["type"] == "d":  # 字典
                        _dictData[_cellData["parName"]] = dict(self.structDict(_cell))
                    elif _cellData["type"] == "l":  # 列表
                        _dictData[_cellData["parName"]] = list(self.structList(_cell))
        return _dictData

    # 构建列表
    def structList(self, cell_):
        _listData = []
        for _cell in cell_.data["cellList"]:
            if hasattr(_cell, 'data'):
                _cellData = _cell.data
                if utils.excelUtils.isParNameData(_cellData["parName"]):  # 如果当前是个数据,数组的数据名称没有实际意义,就是个数据类型的标示
                    _listData.append(_cellData["value"])
                elif utils.excelUtils.isParNameStructure(_cellData["parName"]):
                    if _cellData["type"] == "d":  # 字典
                        _listData.append(dict(self.structDict(_cell)))
                    elif _cellData["type"] == "l":  # 列表
                        _listData.append(list(self.structList(_cell)))
        return _listData

    # cell里面是一个数据名,那么取得它的数据信息并且返回
    def getCellParData(self, col_, row_):
        _dataInfo = None
        _cellStr = self.getStrByCr(col_, row_)
        if utils.excelUtils.isParNameData(_cellStr):  # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
            _cell = self.cells[col_][row_]  # 获取格子
            _dataInfo = {"parName": _cellStr, "type": _cellStr[0:1]}  # 格子中写入数据
            _cellNextColStr = self.getStrByCr(col_ + 1, row_)
            if not _cellNextColStr or (_cellNextColStr == "" and not _dataInfo["type"] == "s"):
                raise TypeError(utils.excelUtils.crToPos(col_ + 1, row_) + " 没有值")
            if _dataInfo["type"] == "i":
                _dataInfo["value"] = utils.convertUtils.strToInt(_cellNextColStr)
            elif _dataInfo["type"] == "f":
                _dataInfo["value"] = utils.convertUtils.strToFloat(_cellNextColStr)
            elif _dataInfo["type"] == "b":
                _cellValue = _cellNextColStr
                if _cellValue == 1.0 or _cellValue.lower() == "t" or _cellValue.lower() == "true" or _cellValue == "1":
                    _dataInfo["value"] = True
                elif _cellValue == 0.0 or _cellValue.lower() == "f" or _cellValue.lower() == "false" or _cellValue == "0":
                    _dataInfo["value"] = True
                else:
                    raise TypeError(
                        utils.excelUtils.crToPos(col_, row_) + " 所在为一个Boolean值,只能是1/0 true/false t/f 中的一个"
                    )
            elif _dataInfo["type"] == "u" or _dataInfo["type"] == "t" or _dataInfo["type"] == "s":
                _dataInfo["value"] = _cellNextColStr

            _cell.data = _dataInfo
            if int(col_ + 2) < self.maxCol:  # <再往后都是空白><但是可能往后超过了列数限制-判断一下>
                for _currentValueCol in range(col_ + 2, self.maxCol):  # 当前行向后找
                    if not (self.getStrByCr(_currentValueCol, row_) == ""):  # 如果出现不为空的格子,报错
                        raise TypeError(
                            utils.excelUtils.crToPos(
                                _currentValueCol, row_
                            ) + " 不能有值,因为 " + utils.excelUtils.crToPos(
                                col_, row_
                            ) + " 是一个数据")
            # print("data : " + str(_dataInfo))
        return _dataInfo

    def getCellStructureData(self, col_, row_):  # cell里面是一个结构名,获取它所持有的数据
        _dataInfo = None
        _cellStr = self.getStrByCr(col_, row_)
        if utils.excelUtils.isParNameStructure(_cellStr):  # 当前的字段名,字典和列表,字段名后面不可以有任何字符串
            _cell = self.cells[col_][row_]  # 获取格子
            _dataInfo = {"parName": _cellStr, "type": _cellStr[0:1], "cellList": []}  # 获取它的结构 格子中写入数据
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
                    raise TypeError(
                        utils.excelUtils.crToPos(
                            _currentValueCol, row_
                        ) + " 不能有值,因为 " + utils.excelUtils.crToPos(
                            col_, row_
                        ) + " 是一个列表命名/字典命名")
            # print('_dataInfo : ' + str(_dataInfo))
        return _dataInfo
