#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *


class SwiftCodeAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SwiftCodeAnalyse, self).create()
        self.analyseFolder("Universal")

    def destory(self):
        super(SwiftCodeAnalyse, self).destory()

    # 根据给定文件夹，遍历分析每一个文件
    def analyseFolder(self, folderName_: str):
        _swiftCodeFolder = fileUtils.getPath(self.resPath, folderName_)
        _filePathDict = folderUtils.getFilePathKeyValue(_swiftCodeFolder, [".swift"])
        for _k, _v in _filePathDict.items():
            _keyName = _k
            print(str(_keyName).ljust(40) + ":" + str(_v))  # 名称 -> 路径 关系输出
            if _keyName == "2 - MyGameCoordinator.swift":
                _codeWithComment = fileUtils.readFromFile(_v)
                _codeWithOutComment = codeUtils.removeComment("swift", _codeWithComment)
                for _idx, _line in list(enumerate(_codeWithOutComment.split("\n"))):
                    print(str(_idx).ljust(3) + ":" + str(_line))
