# !/usr/bin/env python3
# excel解析工具
import sys
import os
import xlrd
import xlsxwriter
from utils import fileUtils
from utils import pyUtils
from utils.excelUtil.DictSheet import DictSheet
from utils.excelUtil.DictListSheet import DictListSheet
from utils.excelUtil.ListSheet import ListSheet
from utils.excelUtil.CMDSheet import CMDSheet
from utils.excelUtil.KVSheet import KVSheet
from utils.excelUtil.StateSheet import StateSheet


# 将一个Excel格式规范化
#   固定几个类型的Sheet
class WorkBook(object):
    def __init__(self):
        self.currentWorkBook = None
        self.readPath = None
        self.savePath = None
        self.sheetDict = {}

    def printSelf(self):
        print("WorkBook".ljust(20) + " : " + os.path.basename(self.readPath))
        print("  readForm".ljust(20) + " : " + self.readPath)
        print("  writeTo".ljust(20) + " : " + self.savePath)
        print("  sheets".ljust(20) + " -----------------------------------------")
        for _sheetName in self.sheetDict:
            self.getSheetByName(_sheetName).printSelf()

    def initBlankWorkBook(self):
        self.currentWorkBook = None

    def initWithWorkBook(self, filePath_):
        # print("> WorkBook > initWithWorkBook : " + filePath_)
        if not os.path.isfile(filePath_):
            print('WorkBook.initWithWorkBook 文件路径不存在 : ' + filePath_)
            sys.exit()

        # 只读的那个
        self.currentWorkBook = xlrd.open_workbook(filePath_)

        # # Notice
        # _typeDict = {}
        # _typeDict["currentWorkBook"] = self.currentWorkBook
        # self.currentWorkBook = _typeDict.get("currentWorkBook", xlrd.Workbook())

        _baseFileName = os.path.basename(filePath_)
        self.readPath = filePath_
        # 切后缀，重新拼接
        self.savePath = fileUtils.pathWithOutSuffix(filePath_) + "_save.xlsx"

        for _sheetName in self.currentWorkBook.sheet_names():
            if _sheetName.endswith("<list>"):
                _currentSheet = ListSheet()
            elif _sheetName.endswith("<dictlist>"):
                _currentSheet = DictListSheet()
            elif _sheetName.endswith("<dict>"):
                _currentSheet = DictSheet()
            elif _sheetName.endswith("<kv>"):
                _currentSheet = KVSheet()
            elif _sheetName.endswith("<proto>"):
                raise pyUtils.AppError("SheetName : '" + _sheetName + "',prefix is not supports")
            elif _sheetName.endswith("<relation>"):
                raise pyUtils.AppError("SheetName : '" + _sheetName + "',prefix is not supports")
            elif _sheetName.endswith("<state>"):
                _currentSheet = StateSheet()
            elif _sheetName.endswith("<cmd>"):
                _currentSheet = CMDSheet()
            else:
                raise pyUtils.AppError("SheetName : '" + _sheetName + "',prefix is not supports")

            _currentSheet.initWithSheet(
                self.currentWorkBook.sheet_by_name(_sheetName),
                _sheetName.split("<")[0]  # 去掉类型，指定的部分，为sheetName
            )
            self.addSheet(_currentSheet)

    # search --------------------------------------------------------------------------------------------------------
    def getSheetByName(self, sheetName_):
        # # Notice 字典里取得对象,指定他的类型.
        return self.sheetDict[sheetName_]

    # save ----------------------------------------------------------------------------------------------------------
    def save(self):
        self.saveToPath(self.savePath)

    def saveToPath(self, filePath_):
        self.getWriteWorkBook(filePath_).close()

    def getWriteWorkBook(self, savePath_):
        # 创建一个可写文件
        _writeWorkbook = xlsxwriter.Workbook(savePath_)
        # 循环 只读 的 workBook
        for _sheetName in self.sheetDict:
            # 在 写入 workBook 中 创建 写入Sheet
            _currentWriteSheet = _writeWorkbook.add_worksheet(_sheetName)
            # 读取一个 sheet
            _currentReadSheet = self.getSheetByName(_sheetName)
            # 将 只读文件的内容 拷贝 到 写入文件
            _currentReadSheet.copyToWriteSheet(_currentWriteSheet)
        return _writeWorkbook

    # change --------------------------------------------------------------------------------------------------------
    def addSheet(self, sheet_):
        if sheet_.sheetName in self.sheetDict:
            raise Exception("WorkBook 中 已经存在 名称为 : " + sheet_.sheetName + " 的Sheet")
        else:
            self.sheetDict[sheet_.sheetName] = sheet_
        return sheet_

    # 转换成jsonDict
    def toJsonDict(self):
        _excelDict = {}
        for _sheetName in self.sheetDict:
            _excelDict[_sheetName] = self.sheetDict[_sheetName].toJsonDict()
        return _excelDict

    # 写入文件夹
    def toJsonFile(self, locateFolderPath_: str):
        for _sheetName in self.sheetDict:
            print(" " * 4 + " -> " + _sheetName + " -> 开始解析 A")
            _sheet = self.sheetDict[_sheetName]
            _sheet.toJsonFile(locateFolderPath_)
            print(" " * 4 + " <- " + _sheetName + " <- 解析完成 V")
