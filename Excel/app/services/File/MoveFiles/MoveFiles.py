#!/usr/bin/env python3
# Created by jiasy at 2020/9/9
from utils import folderUtils
from utils import sysUtils
from utils import fileCopyUtils
import os
import shutil

from Excel.ExcelBaseInService import ExcelBaseInService


class MoveFiles(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "Replace": {
                "sourceFolder": "源",
                "targetFolder": "目标",
            },
            "Override": {
                "sourceFolder": "源",
                "targetFolder": "目标",
            },
        }

    def create(self):
        super(MoveFiles, self).create()

    def destory(self):
        super(MoveFiles, self).destory()

    # 拷贝，只拷贝并替换已经存在的文件
    def replaceFiles(self, typeFilters_: list, sourceFolderPath_: str, targetFolderPath_: str):
        _filePathDict = folderUtils.getFilePathKeyValue(targetFolderPath_, typeFilters_)
        for _fileName, _filePath in _filePathDict.items():
            _shortPath = _filePath.split(targetFolderPath_)[1]
            _tarfilePath = targetFolderPath_ + _shortPath
            _sourcefilePath = sourceFolderPath_ + _shortPath
            # 存在这文件，就拷贝
            if os.path.exists(_sourcefilePath):
                print('        copy : ' + str(_fileName))
                shutil.copy(_sourcefilePath, _tarfilePath)
            else:
                print('x-      pass : ' + str(_fileName))

    def Replace(self, dParameters_: dict):
        _sourceFolderPath = sysUtils.folderPathFixEnd(dParameters_["sourceFolder"])
        _targetFolderPath = sysUtils.folderPathFixEnd(dParameters_["targetFolder"])
        _filters = dParameters_["filters"]  # 过滤项
        _filePathDict = folderUtils.getFilePathKeyValue(_sourceFolderPath, _filters)
        for _, _filePath in _filePathDict.items():  # 存在文件，才拷贝
            _shortPath = _filePath.split(_sourceFolderPath)[1]
            _tarfilePath = _targetFolderPath + _shortPath
            _sourcefilePath = _sourceFolderPath + _shortPath
            if os.path.exists(_tarfilePath):
                print('        copy to : ' + str(_tarfilePath))
                shutil.copy(_sourcefilePath, _tarfilePath)
            else:
                print('x-      pass : ' + str(_sourcefilePath))

    def Override(self, dParameters_: dict):
        _sourceFolderPath = sysUtils.folderPathFixEnd(dParameters_["sourceFolder"])
        _targetFolderPath = sysUtils.folderPathFixEnd(dParameters_["targetFolder"])
        _filters = dParameters_["filters"]  # 过滤项
        _filePathDict = folderUtils.getFilePathKeyValue(_sourceFolderPath, _filters)
        for _, _filePath in _filePathDict.items():  # 存不存在都拷贝
            _shortPath = _filePath.split(_sourceFolderPath)[1]
            _tarfilePath = _targetFolderPath + _shortPath
            _sourcefilePath = _sourceFolderPath + _shortPath
            print('        copy to : ' + str(_tarfilePath))
            shutil.copy(_sourcefilePath, _tarfilePath)


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称
    # Main.excelProcessStepTest(
    #     _baseServiceName,
    #     _subBaseInServiceName,
    #     "Override",
    #     # "Replace",
    #     {  # 所需参数
    #         "sourceFolder": "{resFolderPath}/source",
    #         "targetFolder": "{resFolderPath}/target",
    #         "filters": [".txt", ".png"],
    #     },
    #     {  # 命令行参数
    #         "executeType": "单体测试"
    #     }
    # )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
