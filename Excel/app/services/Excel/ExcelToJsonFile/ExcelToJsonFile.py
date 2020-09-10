#!/usr/bin/env python3
# Created by jiasy at 2020/9/7

from utils import sysUtils
from utils import folderUtils
from utils import fileUtils
import os
from utils.excelUtil import WorkBook

from Excel.ExcelBaseInService import ExcelBaseInService


class ExcelToJsonFile(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "ToJsonFile": {
                "sSourceFolder": "xlsx所在的源",
                "sTargetFolder": "转换成json后，放置于的路径",
            }
        }

    def create(self):
        super(ExcelToJsonFile, self).create()

    def destory(self):
        super(ExcelToJsonFile, self).destory()

    def ToJsonFile(self, dParameters_: dict):
        # 确保路径正确
        _sourceFolderPath = sysUtils.folderPathFixEnd(dParameters_["sSourceFolder"])
        _targetFolderPath = sysUtils.folderPathFixEnd(dParameters_["sTargetFolder"])
        _xlsxFilePathList = folderUtils.getFileListInFolder(_sourceFolderPath, [".xlsx"])
        for _idx in range(len(_xlsxFilePathList)):
            _xlsxFilePath = _xlsxFilePathList[_idx]
            # # 变更执行权限
            # cmdUtils.showXattr(os.path.dirname(_xlsxFilePath))  # Operation not permitted 时放开注释，查阅信息
            # sysUtils.chmod("666","["com.apple.quarantine"]", _xlsxFilePath)
            # xlsx文件 -> 文件夹，包含了将要生成json文件。
            _xlsxFolderPath = fileUtils.getNewNameKeepFolderStructure(
                _sourceFolderPath, _targetFolderPath, _xlsxFilePath
            )
            _currentWorkBook = WorkBook.WorkBook()  # 解析WorkBook
            _currentWorkBook.initWithWorkBook(_xlsxFilePath)
            _currentWorkBook.toJsonFile(_xlsxFolderPath)  # 内容解析成json，写入给定文件夹
            print("    【SUCCESS】 : " + _xlsxFilePath)


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
        "ToJsonFile",
        {  # 所需参数
            "sSourceFolder": "{sResPath}/source",
            "sTargetFolder": "{sResPath}/target"
        },
        {  # 命令行参数
            "sExecuteType": "单体测试"
        }
    )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 命令行参数
            "sExecuteType": "单体测试"
        }
    )
