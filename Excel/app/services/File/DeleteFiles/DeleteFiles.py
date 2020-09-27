#!/usr/bin/env python3
# Created by jiasy at 2020/9/27

from Excel.ExcelBaseInService import ExcelBaseInService
import os
import sys
from utils import sysUtils
from utils import folderUtils
from utils import pyUtils
import shutil


class DeleteFiles(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "DeleteFolder": {
                "deleteFolderPath": "要删除的目录",
            },
            "DeleteFileInFolder": {
                "deleteFolderPath": "要删除的目录",
                "filters": "过滤用的文件后缀列表",
            },
        }

    def create(self):
        super(DeleteFiles, self).create()

    def destory(self):
        super(DeleteFiles, self).destory()

    def checkDeleteFolder(self, deleteFolderPath_: str):
        # 判断是否正在删除根目录。。。
        if deleteFolderPath_.index(os.sep) < 0:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), deleteFolderPath_ + " : 注意！你要删除哪里？")
            sys.exit(1)
        else:
            _deleteSplitLength = len(deleteFolderPath_.split(os.sep)) - 2
            if _deleteSplitLength <= 5:
                # 一般本机的目录结构。为了不错误的删除了内容，进行了一次强制长度判断。太短的路径，不会进行删除
                # /盘符/子盘目录/自定义分类/ -- 移动硬盘的情况
                # /Users/用户/分类(Download、desktop)/自定义分类/ -- 本机目录的情况 <以这个为安全层级数，防止误删除>
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                " : 路径有点儿短，防错误路径，不予执行。。。 : \n    " + deleteFolderPath_
                                )
                sys.exit(1)

    # 删除整个文件夹
    def DeleteFolder(self, dParameters_):
        _deleteFolderPath = sysUtils.folderPathFixEnd(dParameters_["deleteFolderPath"])
        self.checkDeleteFolder(_deleteFolderPath)
        # shutil.rmtree(str(_deleteFolderPath))

    # 删除明确要过滤的内容
    def DeleteFileInFolder(self, dParameters_):
        _deleteFolderPath = sysUtils.folderPathFixEnd(dParameters_["deleteFolderPath"])
        self.checkDeleteFolder(_deleteFolderPath)
        folderUtils.removeFileByFilter(_deleteFolderPath, dParameters_["filters"])


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    # _functionName = "DeleteFolder"
    # _parameterDict = {  # 所需参数
    #     "deleteFolderPath": "/Users/jiasy/Downloads/Slicy Examples/",
    # }

    _functionName = "DeleteFileInFolder"
    _parameterDict = {  # 所需参数
        "deleteFolderPath": "{resFolderPath}/",
        "filters": [".png", ".jpg"],
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
