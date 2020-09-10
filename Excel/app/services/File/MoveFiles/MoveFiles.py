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
                "sSourceFolder": "源",
                "sTargetFolder": "目标",
            },
            "Override": {
                "sSourceFolder": "源",
                "sTargetFolder": "目标",
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
        _sourceFolderPath = sysUtils.folderPathFixEnd(dParameters_["sSourceFolder"])
        _targetFolderPath = sysUtils.folderPathFixEnd(dParameters_["sTargetFolder"])
        _filters = dParameters_["lFilters"]  # 过滤项
        self.replaceFiles(
            _filters,
            _sourceFolderPath,
            _targetFolderPath
        )

    def Override(self, dParameters_: dict):
        _sourceFolderPath = sysUtils.folderPathFixEnd(dParameters_["sSourceFolder"])
        _targetFolderPath = sysUtils.folderPathFixEnd(dParameters_["sTargetFolder"])
        _filters = dParameters_["lFilters"]  # 过滤项
        fileCopyUtils.copyFilesInFolderTo(
            _filters,
            _sourceFolderPath,
            _targetFolderPath
        )


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
    #     #"Replace",
    #     {  # 所需参数
    #         "sSourceFolder": "{sResPath}/source",
    #         "sTargetFolder": "{sResPath}/target",
    #         "lFilters": [".txt", ".png"],
    #     },
    #     {  # 命令行参数
    #         "sExecuteType": "单体测试"
    #     }
    # )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 命令行参数
            "sExecuteType": "单体测试"
        }
    )
