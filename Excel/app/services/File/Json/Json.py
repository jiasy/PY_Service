#!/usr/bin/env python3
# Created by jiasy at 2020/9/9
from utils import folderUtils
from utils import sysUtils
from utils import jsonUtils
from utils import fileUtils
import os
import json
import sys

from Excel.ExcelBaseInService import ExcelBaseInService


class Json(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "MargeJsonDict": {
                "jsonFilePath": "json文件路径",
                "margeJsonDict": "json结构的DictSheet配置",
            },
        }

    def create(self):
        super(Json, self).create()

    def destory(self):
        super(Json, self).destory()

    def MargeJsonFile(self, dParameters_: dict):
        _jsonFilePath = dParameters_["jsonFilePath"]
        _margeJsonFilePath = dParameters_["margeJsonFilePath"]
        _jsonDict = fileUtils.dictFromJsonFile(_jsonFilePath)
        _margeJsonDict = fileUtils.dictFromJsonFile(_margeJsonFilePath)
        _jsonDict = jsonUtils.mergeAToB(_margeJsonDict, _jsonDict)  # 合并
        fileUtils.writeFileWithStr(  # 写回去
            _jsonFilePath,
            str(json.dumps(_jsonDict, indent=4, sort_keys=False, ensure_ascii=False))
        )

    def MargeJsonDict(self, dParameters_: dict):
        _jsonFilePath = dParameters_["jsonFilePath"]
        _margeJsonDict = dParameters_["margeJsonDict"]
        _jsonDict = fileUtils.dictFromJsonFile(_jsonFilePath)
        _jsonDict = jsonUtils.mergeAToB(_margeJsonDict, _jsonDict)  # 合并
        fileUtils.writeFileWithStr(  # 写回去
            _jsonFilePath,
            str(json.dumps(_jsonDict, indent=4, sort_keys=False, ensure_ascii=False))
        )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称

    _functionName = "MargeJsonDict"
    _parameterDict = {  # 所需参数
        "jsonFilePath": "{resFolderPath}/jsconfig.json",
        "margeJsonDict": {
            "exclude": [
                "node_modules",
                ".vscode",
                "library",
                "local",
                "settings",
                "temp"
            ],
            "compilerOptions": {
                "addParameter": "added",  # 添加一个参数
                "target": "es5"  # 修改一个参数
            }
        }
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
