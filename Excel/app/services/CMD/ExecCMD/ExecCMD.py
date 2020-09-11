#!/usr/bin/env python3
# Created by jiasy at 2020/9/8

from utils import sysUtils
from utils import cmdUtils
from utils import pyUtils
import os

from Excel.ExcelBaseInService import ExcelBaseInService


class ExecCMD(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "JustCMD": {  # 没有参数的方法，比如 tree ,ls -l 等
                "CMD": "指明执行的命令",
                "execFolderPath": "执行方法时的路径",
            },
            "CMDInProject": {  # 网上找的py脚本，直接拖放到工程里。提供这样一个方式来执行脚本。
                "toolName": "工具名称，因为在工程内，所以不用指定路径。但是，路径是要严格按照规范放置于子服务的res内",
                "parameterList": "参数列表，按照DictSheet的规则解析出来的JsonDict",
            },
            "ToolsInSystem": {  # 电脑里的工具，或者是支持命令行的App(比如CocosCreator、Unity、Spine、TexturePacker等)
                "toolPathOrTooName": "已经配置好的系统命令，或者系统中的工具路径",
                # 参数列表，一般两种 键值对 或 纯值。这两种需要做到混合。某些工具的键是可以重复的，所以，不能使用平表来做。
                # 使用数组来设置参数，支持纯值和键值，顺序严格按照数据的摆放顺序排列参数。
                "parameterList": "参数列表，按照DictSheet的规则解析出来的JsonDict",
            },
        }

    def create(self):
        super(ExecCMD, self).create()

    def destory(self):
        super(ExecCMD, self).destory()

    # 执行无参数的命令
    def JustCMD(self, dParameters_: dict):
        _cmdStr = str(dParameters_["CMD"])
        _execFolderPath = sysUtils.folderPathFixEnd(dParameters_["execFolderPath"])  # 路径需要确保后面有/
        cmdUtils.doStrAsCmd(_cmdStr, _execFolderPath, True)

    # 执行工程内的有参数的命令
    def CMDInProject(self, dParameters_: dict):
        _toolName = str(dParameters_["toolName"])
        _toolPath = os.path.join(self.subResPath, _toolName, _toolName + ".py")
        _cmdStr = "python " + _toolPath + " "
        if "parameterList" in dParameters_:  # 列表形式的参数需求
            _parameterList = dParameters_["parameterList"]
            for _i in range(len(_parameterList)):
                _parameterElement = _parameterList[_i]
                if isinstance(_parameterElement, dict):  # 键值对形式的参数
                    _cmdStr += "--" + _parameterElement["key"] + " '" + _parameterElement["value"] + "' "
                else:  # 纯值形 参数
                    _cmdStr += "'" + str(_parameterElement) + "' "
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "必须有 parameterList 参数")
        cmdUtils.doStrAsCmd(
            _cmdStr,
            os.path.dirname(_toolPath),  # 工具所在目录执行工具
            True
        )

    # 执行系统中配置好的，或者是某些录几个下的一些工具
    def ToolsInSystem(self, dParameters_: dict):
        _toolPathOrTooName = str(dParameters_["toolPathOrTooName"])  # 工具路径，或者是全局已经配置好的名称
        _execFolderPath = sysUtils.folderPathFixEnd(dParameters_["execFolderPath"])  # 路径需要确保后面有/
        _cmdStr = _toolPathOrTooName + " "
        # 列表形式的参数需求
        if "parameterList" in dParameters_:
            _parameterList = dParameters_["parameterList"]
            for _i in range(len(_parameterList)):
                _parameterElement = _parameterList[_i]
                if isinstance(_parameterElement, dict):  # 键值对形式的参数
                    _cmdStr += "--" + _parameterElement["key"] + " '" + _parameterElement["value"] + "' "
                else:  # 列表形式的参数
                    _cmdStr += "'" + str(_parameterElement) + "' "
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "必须有 parameterList 参数")
        cmdUtils.doStrAsCmd(
            _cmdStr,
            _execFolderPath,
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

        # "JustCMD",
        # {  # 所需参数
        #     "CMD": "PWD",
        #     "execFolderPath": "{resFolderPath}",  # 在子服务对应的资源目录中执行代码
        # },

        "CMDInProject",
        {  # 所需参数，{resFolderPath}为当前子服务对应的资源文件路径
            "toolName": "plistUnpack",
            "parameterList": [
                "{resFolderPath}/plistUnpack/pack"
            ]
        },

        {  # 命令行参数
        }
    )

    # Main.execExcelCommand(
    #     _baseServiceName, _subBaseInServiceName,  # 取得要测试的Excel地址用。服务配置在取得的Excel中，这里不用配置
    #     {  # 命令行参数
    #         "executeType": "单体测试"
    #     }
    # )
