# !/usr/bin/env python3
import utils
import os
import json
from utils import excelUtils
from utils import pyUtils
from utils.excelUtil.Cell import Cell
from enum import Enum


class SheetType(Enum):
    NORMAL = 1
    LIST = 1
    DICT = 2
    KV = 3
    PROTO = 4
    STATE = 5
    WORKFLOW = 6


class Sheet:
    def __init__(self):
        # print("> > > >Sheet_init")
        self.sheetName = None
        self.sheetType = SheetType.NORMAL
        self.cells = []
        self.maxCol = None
        self.maxRow = None
        # 一些附加数据
        self.data = None
        pass

    def printSelf(self):
        print("Sheet Name".ljust(20) + " : " + self.sheetName)
        print("col : ".ljust(20) + str(self.maxCol))
        print("row : ".ljust(20) + str(self.maxRow))
        self.printSheet()

    # 初始化一个Sheet,利用一个读取到的Sheet来创建
    def initWithSheet(self, targetSheet_, sheetName_):
        # print("> > Sheet > initWithSheet")
        self.sheetName = sheetName_
        self.maxCol = targetSheet_.ncols
        self.maxRow = targetSheet_.nrows

        for _colNum in range(targetSheet_.ncols):
            self.cells.append([])
            for _rowNum in range(targetSheet_.nrows):
                _currentCell = Cell(targetSheet_.cell(_rowNum, _colNum).value, _colNum, _rowNum,
                                    excelUtils.crToPos(_colNum, _rowNum))
                self.cells[_colNum].append(_currentCell)

    # 利用名称,初始化一个空sheet
    def initWithName(self, sheetName_):
        # print("> > Sheet > initBlankSheet")
        self.sheetName = sheetName_
        self.maxCol = 0
        self.maxRow = 0

    # print------------------------------------------------------------------------------------------------------------
    def printSheet(self):
        print("> > Sheet > printSheet---------------" + self.sheetName + "---------------")
        _printStr = "<^> - " + str("").ljust(3) + " : "
        for _colNum in range(self.maxCol):
            _printStr += str(_colNum) + "-" + excelUtils.cToPos(_colNum).ljust(10) + ","
        print(_printStr)
        for _rownum in range(self.maxRow):
            self.printRow(_rownum)

    # for _colNum in range(self.maxCol):
    #	 self.printCol(_colNum)

    def printCol(self, col_):
        _printStr = "col - " + str(col_).ljust(3) + " : "
        _splitStr = ","
        for _row in range(self.maxRow):
            _printStr += self.cells[col_][_row].strValue.ljust(10) + _splitStr
        print(_printStr)

    def printRow(self, row_):
        _printStr = "row - " + str(row_).ljust(3) + " : "
        _splitStr = ","
        for _col in range(self.maxCol):
            _printStr += self.cells[_col][row_].strValue.ljust(10) + _splitStr
        print(_printStr)

    # search-----------------------------------------------------------------------------------------------------------
    def getCellsByStr(self, str_):
        # print("> > Sheet > getCrByStr : " + str_)
        _cellList = []
        # Notice string 和 unicode 相互转化
        _uniStr = str_.decode('utf-8')
        for _row in range(self.maxRow):
            for _col in range(self.maxCol):
                if self.cells[_col][_row].value == _uniStr:
                    _cellList.append(self.cells[_col][_row])
        if len(_cellList) == 0:
            print("Sheet.getCrByStr " + str_ + " 不存在")

        return _cellList

    # get--------------------------------------------------------------------------------------------------------------
    def getStrByPos(self, posStr_):
        # print("> > Sheet > getStrByPos : " + posStr_)
        _col, _row = excelUtils.posToCr(posStr_)
        return self.getStrByCr(_col, _row)

    def getStrByCr(self, col_, row_):
        # print("> > Sheet > getStrByCr :  _c: " + str(col_) + " _r: " + str(row_))
        if row_ >= self.maxRow:
            raise TypeError("Sheet.getStrByPos posStr_ : " + str(row_) + " 行数越界 " + str(self.maxRow))
        if col_ >= self.maxCol:
            raise TypeError("Sheet.getStrByPos posStr_ : " + str(col_) + " 列数越界 " + str(self.maxCol))
        _backValue = self.cells[col_][row_].strValue
        return _backValue

    # set--------------------------------------------------------------------------------------------------------------
    def setStrToPos(self, str_, posStr_):
        _col, _row = excelUtils.posToCr(posStr_)
        self.setStrToCr(str_, _col, _row)

    def setStrToCr(self, str_, col_, row_):
        # print("> > Sheet > setStrToCr : " + str_ + " _c: " + str(col_) + " _r: " + str(row_))
        # 这里注意-有先后,先列拓展,后行拓展
        if col_ >= self.maxCol:
            self.extendCol(col_)
        if row_ >= self.maxRow:
            self.extendRow(row_)
        self.cells[col_][row_].write(str_)

    # copy-------------------------------------------------------------------------------------------------------------
    def copyToWriteSheet(self, writeSheet_):
        for _row in range(self.maxRow):
            for _col in range(self.maxCol):
                writeSheet_.write(_row, _col, self.cells[_col][_row].value)

    # extends----------------------------------------------------------------------------------------------------------
    def extendCol(self, col_):
        # 这里注意-有先后,先列拓展,后行拓展
        # print("> > Sheet > extendCol : " + str(col_))
        for _col in range(int(self.maxCol), int(col_ + 1)):
            print("_col : " + str(_col))
            self.cells.append([])
            for _row in range(self.maxRow):
                self.cells[_col].append(Cell("", _col, _row, excelUtils.crToPos(_col, _row)))
        self.maxCol = len(self.cells)

    def extendRow(self, row_):
        # print("> > Sheet > extendRow")
        # 这里注意-有先后,先列拓展,后行拓展
        for _col in range(self.maxCol):
            for _row in range(int(self.maxRow), int(row_ + 1)):
                self.cells[_col].append(Cell("", _col, _row, excelUtils.crToPos(_col, _row)))
        self.maxRow = len(self.cells[self.maxCol - 1])

    def toJsonDict(self):
        raise pyUtils.AppError("Sheet -> toJsonDict must override")
        return

    def toJsonFile(self, locateFolderPath_: str):
        _jsonDict = self.toJsonDict()
        _jsonFilePath = os.path.join(locateFolderPath_, self.sheetName + ".json")
        utils.fileUtils.writeFileWithStr(
            _jsonFilePath,
            str(json.dumps(_jsonDict, indent=4, sort_keys=False, ensure_ascii=False))
        )
