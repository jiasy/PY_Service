#!/usr/bin/env python3
# Created by jiasy at 2020/9/28

from Excel.ExcelBaseInService import ExcelBaseInService
import os
from utils import sysUtils


class BuildUnity(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "Func": {
                "parameterA": "A参数",
                "parameterB": "B参数",
            },
        }

    def create(self):
        super(BuildUnity, self).create()

    def destory(self):
        super(BuildUnity, self).destory()

    def Func(self, dParameters_):
        _parameterAPath = sysUtils.folderPathFixEnd(dParameters_["parameterA"])


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    _functionName = "Func"
    _parameterDict = {  # 所需参数
        "parameterA": "{resFolderPath}/A文件",
        "parameterB": "{resFolderPath}/B文件",
    }

    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        _parameterDict,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
