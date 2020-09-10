#!/usr/bin/env python3

# 通过Excel配置脚本执行的步骤
#   通过ExcelApp每次执行一个xlsx
#   dGlobalDict 为一全局参数的平表，通过命令行参数修改其中内容，用于保存全局上下文，或者是jenkins的设置/命令行执行替换掉某些参数[test/publish]。
# 全局 dGlobalDict有一个固定格式。
# 每一个功能有一个固定格式。
# CMD也可以执行命令行，不过这里单纯的执行和输出，无法交互。执行命令的时候，想保存上下文，可以通过读写一个固定名称json文件来实现。

from base.supports.App.App import App
from utils import strUtils
from utils import jsonUtils
from utils import pyUtils
from utils import listUtils
from utils import cmdUtils
from utils.excelUtil.WorkBook import WorkBook
from utils.excelUtil.Sheet import SheetType
import os
import sys
import json


class ExcelApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        return

    # 运行 Excel
    def runExcel(self, excelPath_: str, pwd_: str, cmdDict_: dict = {}):
        print("执行excel配置流程 :" + excelPath_)
        # cmdUtils.showXattr(os.path.dirname(excelPath_))  # Operation not permitted 时放开注释，查阅信息
        # sysUtils.chmod("666", ["com.apple.quarantine"], excelPath_)  # 按照信息删除对应的限制信息
        # Excel 依旧权限不够，强制重新开启 Finder。
        _currentWorkBook = WorkBook()
        _currentWorkBook.initWithWorkBook(excelPath_)
        for _sheetName in _currentWorkBook.sheetDict:
            _sheet = _currentWorkBook.sheetDict[_sheetName]
            if _sheet.sheetType != SheetType.CMD:
                self.info.raiseERR(
                    pyUtils.getCurrentRunningFunctionName() + "\n" +
                    "ExcelApp -> runExcel : " + _sheetName +
                    " 不是 CMD 类型"
                )
            _sheetJsonDict = _sheet.toJsonDict()
            print(str(_sheetName) + " 配置解析成功")
            if ("dGlobalDict" in _sheetJsonDict) and ("lProcessSteps" in _sheetJsonDict):
                _globalDict = _sheetJsonDict["dGlobalDict"]  # 全局参数
                _cmdInfoDict = {"__folder__": os.path.dirname(excelPath_), "__pwd__": pwd_}
                for _key in _globalDict:
                    _value = _globalDict[_key]  # 遍历参数，获取值
                    _globalDict[_key] = strUtils.replaceKeyToValueInTemplate(_cmdInfoDict, _value)  # 将运行环境替换到全局变量中
                jsonUtils.mergeAToB(cmdDict_, _globalDict)  # 命令行覆盖掉参数
                self.runServiceByJsonDict(_sheetJsonDict)
                break  # 只执行出现的第一个WORKFLOW页
            else:
                self.info.raiseERR(
                    pyUtils.getCurrentRunningFunctionName() + "\n" +
                    "ExcelApp -> runExcel : " + _sheetName +
                    " 参数配置必须包含 dGlobalDict lProcessSteps"
                )

    # 通过Json文件的内容来执行服务
    def runServiceByJsonDict(self, sheetAndCmdDict_: dict):
        self.dataSetCache = {}  # 数据缓存对象
        # 替换参数 ------------------------------------------------------------------------------------------------------
        _globalDict = sheetAndCmdDict_["dGlobalDict"]  # 全局参数
        _pathToSheetAndCmdDict = "excelData"  # 缓存字典的键
        _changeList = self.sm.dc.setValueToDataPath(_pathToSheetAndCmdDict, sheetAndCmdDict_, self.dataSetCache)
        for _idx in range(len(_changeList)):  # 遍历值变化过的路径
            _changePath = _changeList[_idx]
            _changeValue = self.sm.dc.getValueByDataPath(_changePath, self.dataSetCache)  # 通过变化过的路径，获取变化过的值
            if isinstance(_changeValue, str):  # 变化后的值是字符串的话，尝试替换字符串值
                _convertedStr = strUtils.replaceKeyToValueInTemplate(_globalDict, _changeValue)  # 字典内容替换模板
                if "{" in _convertedStr and "}" in _convertedStr:  # 没有替换的时候，会有{x}这样的字符串残留
                    self.info.raiseERR(
                        pyUtils.getCurrentRunningFunctionName() + "\n" +
                        _changePath + " : " + _convertedStr + "。可能有未转换的数据残留"
                    )
                self.sm.dc.setValueToDataPath(_changePath, _convertedStr, self.dataSetCache)  # 将变换后的值写回数据缓存
        _sheetAndCmdDict = self.sm.dc.dataSetToJsonDict(_pathToSheetAndCmdDict, self.dataSetCache)  # 将缓存转换回json字典对象
        # 流程步骤 ------------------------------------------------------------------------------------------------------
        _processSteps = _sheetAndCmdDict["lProcessSteps"]  # 获取流程步骤
        for _idx in range(len(_processSteps)):  # 输出参数，校验流程
            _processStep = _processSteps[_idx]
            if ("dServiceInfo" in _processStep) and ("dParameters" in _processStep):
                _baseServiceName = _processStep["dServiceInfo"]["sBaseService"]  # 当前进行的参数
                _baseInServiceName = _processStep["dServiceInfo"]["sBaseInService"]
                _functionName = _processStep["dServiceInfo"]["sFunctionName"]
                _comment = _processStep["dServiceInfo"]["sComment"]
                _parameterDict = _processStep["dParameters"]
                # 子服务是否存在指定功能的判断
                _subBaseInService = self.switchTo(_baseServiceName, _baseInServiceName)
                if not _subBaseInService:
                    self.info.raiseERR(
                        pyUtils.getCurrentRunningFunctionName() + "\n" +
                        _baseServiceName + " 不存在 " + _baseInServiceName
                    )
                if not _subBaseInService.checkFunction(_functionName):
                    self.info.raiseERR(
                        pyUtils.getCurrentRunningFunctionName() + "\n" +
                        _baseServiceName + "." + _baseInServiceName + " 不存在 " + _functionName
                    )
                _parameterErrorInfo = _subBaseInService.checkParameters(_functionName, _parameterDict)
                if _parameterErrorInfo:
                    self.info.raiseERR(
                        pyUtils.getCurrentRunningFunctionName() + "\n" +
                        _baseServiceName + "." + _baseInServiceName + " 参数不正确 " + _parameterErrorInfo
                    )

                print(  # 输出分割线，标示当前内容
                    "[" + str(_idx + 1) + "] " +
                    _baseServiceName + " -> " + _baseInServiceName +
                    " " + " ~ " * 30 + "【" + _comment + "】"
                )
                print(" " * 4 + " Global ")  # 使用参数打印
                for _key in _globalDict:
                    print(" " * 8 + _key + " : " + _globalDict[_key])
                print(" " * 4 + " parameter ")
                for _key in _parameterDict:
                    _value = _parameterDict[_key]
                    if isinstance(_value, list):
                        print(" " * 8 + _key + " (" + str(len(_value)) + ") :")
                        listUtils.printList(_value, " " * 12)
                    elif isinstance(_value, dict):
                        print(" " * 8 + _key + " : ")
                        print(" " * 12 + str(json.dumps(_value, indent=4, sort_keys=False, ensure_ascii=False)))
                    else:
                        print(" " * 8 + _key + " : " + _parameterDict[_key])
            else:
                self.info.raiseERR(
                    pyUtils.getCurrentRunningFunctionName() + "\n" +
                    "[" + str(_idx) + "]" + " 参数配置必须包含 dServiceInfo dParameters"
                )

        for _idx in range(len(_processSteps)):  # 执行流程
            _processStep = _processSteps[_idx]
            _baseServiceName = _processStep["dServiceInfo"]["sBaseService"]  # 当前进行的参数
            _baseInServiceName = _processStep["dServiceInfo"]["sBaseInService"]
            _functionName = _processStep["dServiceInfo"]["sFunctionName"]
            _comment = _processStep["dServiceInfo"]["sComment"]
            _parameterDict = _processStep["dParameters"]
            print("<" + str(
                _idx + 1
            ) + "> " + _comment + " - " * 20 + "【" + _baseServiceName + " -> " + _baseInServiceName + "】")
            _subBaseInService = self.switchTo(_baseServiceName, _baseInServiceName)

            try:
                _subBaseInService.doExcelFunc(_functionName, _parameterDict)
            except Exception as e:
                print("x-x x-x x-x x-x x-x x-x x-x [ x-x ERROR x-x ] x-x x-x x-x x-x x-x x-x x-x")
                self.info.raiseERR(pyUtils.getCurrentRunningFunctionName() + "\n" + e.args)

    # 切换到那个服务的，那个子服务上
    def switchTo(self, sBaseService_: str, sBaseInService_: str):
        self.sm.switchRunningServices([])  # 清理原有
        self.sm.switchRunningServices([sBaseService_])  # 重新构建
        _baseService = self.sm.getServiceByName(sBaseService_)
        _baseInService = _baseService.getSubClassObject(sBaseInService_)
        if _baseInService:
            return _baseInService
        else:
            sys.exit(1)


if __name__ == "__main__":
    # res下的Excel文件
    _excelFileName = "ExecSample"
    # excel驱动脚本
    _excelCommandPath = os.path.realpath(os.path.join(
        os.path.realpath(__file__),  # ExcelApp.py 路径
        os.pardir,  # Excel Folder
        os.pardir,  # PY_Service Folder
        "ExcelCommand.py"  # 执行脚本名
    ))
    # 当前执行目录
    _resFolderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")
    # 拼接驱动样例的命令
    _sampleExcelCommand = "python " + _excelCommandPath + \
                          " --sProjectFolderPath " + _resFolderPath + \
                          " --excelPath " + _excelFileName + ".xlsx" + \
                          " --executeType 工作流测试"
    # 执行命令
    cmdUtils.doStrAsCmd(
        _sampleExcelCommand,  # 执行命令行驱动 Excel 工作流配置
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "res"),  # Excel 对应的 res 文件夹内执行
        True
    )
