#!/usr/bin/env python3
from base.supports.App.App import App
from utils import *
from utils.excelUtil.WorkBook import WorkBook
from utils.excelUtil.Sheet import SheetType
import json


class ExcelApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        self.currentSheetDict = None
        return

    # 运行 Excel
    def runExcel(self, excelPath_: str, cmdDict_: dict = {}):
        _currentWorkBook = WorkBook()
        _currentWorkBook.initWithWorkBook(excelPath_)
        for _sheetName in _currentWorkBook.sheetDict:
            _sheet = _currentWorkBook.sheetDict[_sheetName]
            if _sheet.sheetType != SheetType.WORKFLOW:
                raise TypeError("ExcelApp -> runExcel : " + _sheetName + " 不是 WORKFLOW 类型")
            _sheetJsonDict = _sheet.toJsonDict()
            if ("dGlobalDict" in _sheetJsonDict) and ("lProcessSteps" in _sheetJsonDict):
                jsonUtils.mergeAToB(cmdDict_, _sheetJsonDict["dGlobalDict"])  # 命令行覆盖掉参数
                self.runServiceByJsonDict(_sheetJsonDict)  # 只执行出现的第一个WORKFLOW页
            else:
                raise TypeError("ExcelApp -> runExcel : " + _sheetName + " 参数配置必须包含 dGlobalDict lProcessSteps")
            return

    # 通过Json文件的内容来执行服务
    def runServiceByJsonDict(self, sheetAndCmdDict_: dict):
        self.dataSetCache = {}  # 数据缓存对象
        _globalDict = sheetAndCmdDict_["dGlobalDict"]  # 全局参数
        _pathToSheetAndCmdDict = "excelData"  # 缓存字典的键
        _changeList = self.sm.dc.setValueToDataPath(_pathToSheetAndCmdDict, sheetAndCmdDict_, self.dataSetCache)
        for _idx in range(len(_changeList)):  # 遍历值变化过的路径
            _changePath = _changeList[_idx]
            _changeValue = self.sm.dc.getValueByDataPath(_changePath, self.dataSetCache)  # 通过变化过的路径，获取变化过的值
            if isinstance(_changeValue, str):  # 变化后的值是字符串的话，尝试替换字符串值
                _convertedStr = strUtils.replaceKeyToValueInTemplate(_globalDict, _changeValue)  # 字典内容替换模板
                if "{" in _convertedStr and "}" in _convertedStr:  # 没有替换的时候，会有{x}这样的字符串残留
                    raise pyUtils.AppError(_changePath + " : " + _convertedStr + "。可能有未转换的数据残留")
                self.sm.dc.setValueToDataPath(_changePath, _convertedStr, self.dataSetCache)  # 将变换后的值写回数据缓存
        _sheetAndCmdDict = self.sm.dc.dataSetToJsonDict(_pathToSheetAndCmdDict, self.dataSetCache)  # 将缓存转换回json字典对象
        _processSteps = _sheetAndCmdDict["lProcessSteps"]  # 获取流程步骤
        for _idx in range(len(_processSteps)):  # 执行流程
            _processStep = _processSteps[_idx]
            if ("dServiceInfo" in _processStep) and ("dParameters" in _processStep):
                # 当前进行的参数
                _baseServiceName = _processStep["dServiceInfo"]["sBaseService"]
                _baseInServiceName = _processStep["dServiceInfo"]["sBaseInService"]
                _parameterDict = _processStep["dParameters"]
                # 使用参数打印
                print("[" + str(_idx + 1) + "] " + str(_baseServiceName) + " -> " + str(_baseInServiceName) + "-" * 99)
                print(" " * 4 + " Global ")
                for _key in _globalDict:
                    print(" " * 8 + _key + " : " + _globalDict[_key])
                print(" " * 4 + " parameter ")
                for _key in _parameterDict:
                    print(" " * 8 + _key + " : " + _parameterDict[_key])
                # 切换并执行
                _subBaseInService = self.switchTo(_baseServiceName, _baseInServiceName)
                _subBaseInService.doExcelFunc(_parameterDict)
            else:
                raise TypeError(
                    "ExcelApp -> runServiceByJsonDict : " + str(_idx) + " 参数配置必须包含 dServiceInfo dParameters"
                )

    # 切换到那个服务的，那个子服务上
    def switchTo(self, sBaseService_: str, sBaseInService_: str):
        self.sm.switchRunningServices([])  # 清理原有
        self.sm.switchRunningServices([sBaseService_])  # 重新构建
        return self.sm.getServiceByName(sBaseService_).getSubClassObject(sBaseInService_)
