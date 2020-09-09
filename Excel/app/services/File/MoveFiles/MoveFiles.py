#!/usr/bin/env python3
# Created by jiasy at 2020/9/9
from base.supports.Base.BaseInService import BaseInService
import utils
import os
import shutil


class MoveFiles(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(MoveFiles, self).create()

    def destory(self):
        super(MoveFiles, self).destory()

    # 拷贝，只拷贝并替换已经存在的文件
    def replaceFiles(self, typeFilters_: list, sourceFolderPath_: str, targetFolderPath_: str):
        _filePathDict = utils.folderUtils.getFilePathKeyValue(targetFolderPath_, typeFilters_)
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

    def doExcelFunc(self, dParameters_: dict):
        _sourceFolderPath = utils.sysUtils.folderPathFixEnd(dParameters_["sSourceFolder"])
        _targetFolderPath = utils.sysUtils.folderPathFixEnd(dParameters_["sTargetFolder"])
        _filters = dParameters_["lFilters"]  # 过滤项
        _type = dParameters_["sType"]  # 覆盖的类型
        if _type == "override":  # 直接用源保持结构覆盖过去。
            utils.fileCopyUtils.copyFilesInFolderTo(
                _filters,
                _sourceFolderPath,
                _targetFolderPath
            )
        elif _type == "replace":  # 只替源和目标均有的文件。
            self.replaceFiles(
                _filters,
                _sourceFolderPath,
                _targetFolderPath
            )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSp = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSp[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSp[1]  # 切到的后面就是子服务名称
    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 所需参数
            "sSourceFolder": "{sResPath}/source",
            "sTargetFolder": "{sResPath}/target",
            "lFilters": [".txt", "png"],
            "sType": "replace",
        },
        {  # 命令行参数
            "sExecuteType": "单体测试"
        }
    )
