#!/usr/bin/env python3
# Created by jiasy at 2020/9/7
from base.supports.Base.BaseInService import BaseInService
from utils import *
import os
from utils.excelUtil import WorkBook
from utils.excelUtil.Sheet import SheetType


class ExcelToJsonFile(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(ExcelToJsonFile, self).create()

    def destory(self):
        super(ExcelToJsonFile, self).destory()

    def doExcelFunc(self, dParameters_: dict):
        # 确保路径正确
        _sourceFolderPath = sysUtils.folderPathFixEnd(dParameters_["sSourceFolder"])
        _targetFolderPath = sysUtils.folderPathFixEnd(dParameters_["sTargetFolder"])
        _xlsxFilePathList = folderUtils.getFileListInFolder(_sourceFolderPath, [".xlsx"])
        for _idx in range(len(_xlsxFilePathList)):
            _xlsxFilePath = _xlsxFilePathList[_idx]
            # # 变更执行权限
            # sysUtils.chmod("666", _xlsxFilePath)
            # xlsx文件 -> 文件夹，包含了将要生成json文件。
            _xlsxFolderPath = fileUtils.getNewNameKeepFolderStructure(
                _sourceFolderPath, _targetFolderPath, _xlsxFilePath
            )
            _currentWorkBook = WorkBook.WorkBook()  # 解析WorkBook
            _currentWorkBook.initWithWorkBook(_xlsxFilePath)
            _currentWorkBook.toJsonFile(_xlsxFolderPath)  # 内容解析成json，写入给定文件夹
        print("Excel -> Json : ")
        folderUtils.showDirFile(_targetFolderPath, 0, " " * 4)


import Main

if __name__ == "__main__":
    _baseServiceName = "Excel"
    _subBaseInServiceName = "ExcelToJsonFile"
    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 所需参数
            "sSourceFolder": "{sResPath}/source",
            "sTargetFolder": "{sResPath}/target"
        },
        {  # 命令行进行的全局参数修改
            "sPublicType": "test"
        }
    )
