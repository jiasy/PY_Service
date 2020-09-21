#!/usr/bin/env python3
# Created by jiasy at 2020/9/21

from Excel.ExcelBaseInService import ExcelBaseInService
import os
import sys
import json
from utils import fileUtils


class ListSheetFilter(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            # 将列表数据中的部分字段排除，重新放置于一个指定文件夹中[比如，不能将所有的配置都发给客户端]
            "Filter": {
                "jsonFilePath": "DictListSheet 格式生成的 json 文件路径",  # 这个文件是 ListSheet 或 DictListSheet 生成的
                "withOutList": "排除的属性名称列表",
                "toJsonFilePath": "生成的新json文件路径",
            },
        }

    def create(self):
        super(ListSheetFilter, self).create()

    def destory(self):
        super(ListSheetFilter, self).destory()

    def Filter(self, dParameters_: dict):
        _jsonFilePath = dParameters_["jsonFilePath"]
        _toJsonFilePath = dParameters_["toJsonFilePath"]
        _withOutList = dParameters_["withOutList"]
        _jsonList = fileUtils.dictFromJsonFile(_jsonFilePath)
        if not _jsonList or not isinstance(_jsonList, list):
            print("ERROR : " + _jsonFilePath + " 不是一个list或者为空")
            sys.exit(1)

        _type = None
        if isinstance(_jsonList[0], list):  # list模式的二维数组
            _type = "List"
        elif isinstance(_jsonList[0], dict):  # list的模式是对象数组
            _type = "DictList"
        else:
            print("ERROR : " + _jsonFilePath + " 列表元素为意外类型。")

        _backList = []
        if _type == "List":  # 是列表，那么就第一行是字段名，将字段名转换成序号，然后过滤掉
            _parameterList = _jsonList[0]
            _newParameterList = []
            _withOutIdxList = []
            for _i in range(len(_parameterList)):
                if _parameterList[_i] in _withOutList:
                    _withOutIdxList.append(_i)  # 记录要过滤的序号
                else:
                    _newParameterList.append(_parameterList[_i])  # 保留非过滤项
            _backList.append(_newParameterList)
            for _i in range(1, len(_jsonList)):
                _elementList = _jsonList[_i]
                _newElementList = []
                for _j in range(len(_elementList)):
                    if not _j in _withOutIdxList:
                        _newElementList.append(_elementList[_j])
                _backList.append(_newElementList)
        elif _type == "DictList":
            for _i in range(len(_jsonList)):
                _elementDict = _jsonList[_i]
                for _delParameterName in _withOutList:  # 直接删除对应的键值
                    del _elementDict[_delParameterName]
                    _backList = _jsonList

        fileUtils.writeFileWithStr(  # 写回去
            _toJsonFilePath,
            str(json.dumps(_backList, indent=4, sort_keys=False, ensure_ascii=False))
        )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称

    # _functionName = "Filter"
    # _parameterDict = {  # 所需参数
    #     "jsonFilePath": "{resFolderPath}/source/ExcelDictList.json",
    #     "withOutList": ["quality", "registerTime"],
    #     "toJsonFilePath": "{resFolderPath}/separate/ExcelDictListFilter.json"
    # }

    _functionName = "Filter"
    _parameterDict = {  # 所需参数
        "jsonFilePath": "{resFolderPath}/source/ExcelList.json",
        "withOutList": ["headPath"],
        "toJsonFilePath": "{resFolderPath}/separate/ExcelListFilter.json"
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

    # sys.exit(1)

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
