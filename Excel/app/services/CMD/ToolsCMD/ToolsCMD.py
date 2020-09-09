#!/usr/bin/env python3
# Created by jiasy at 2020/9/9
from base.supports.Base.BaseInService import BaseInService
import os
from utils import sysUtils
from utils import cmdUtils
from utils import pyUtils


class ToolsCMD(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(ToolsCMD, self).create()

    def destory(self):
        super(ToolsCMD, self).destory()

    def doExcelFunc(self, dParameters_: dict):
        _toolName = str(dParameters_["sToolName"])
        _toolPath = os.path.join(self.resPath, _toolName, _toolName + ".py")
        _cmdStr = "python " + _toolPath + " "
        # 列表形式的参数需求
        if "lParameterList" in dParameters_:
            _parameterList = dParameters_["lParameterList"]
            for _i in range(len(_parameterList)):
                _parameterElement = _parameterList[_i]
                if isinstance(_parameterElement, dict):  # 键值对形式的参数
                    _cmdStr += "--" + _parameterElement["key"] + " " + _parameterElement["value"]
                else:  # 列表形式的参数
                    _cmdStr += str(_parameterElement) + " "
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "必须有 lParameterList 参数")
        cmdUtils.doStrAsCmd(
            _cmdStr,
            os.path.dirname(_toolPath),  # 工具所在目录执行工具
            True
        )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称
    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 所需参数，{sResPath}为当前子服务对应的资源文件路径
            "sToolName": "plistUnpack",
            "lParameterList": [
                "{sResPath}/plistUnpack/pack"
            ]
        },
        {  # 命令行参数

        }
    )

    # Main.execExcelCommand(
    #     _baseServiceName,
    #     _subBaseInServiceName,
    #     {  # 命令行参数
    #         "sExecuteType": "单体测试"
    #     }
    # )
