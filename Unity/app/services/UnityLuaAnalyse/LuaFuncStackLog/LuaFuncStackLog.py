#!/usr/bin/env python3
# Created by jiasy at 2020/5/21
from base.supports.Base.BaseInService import BaseInService
from utils import *
import re


class LuaFuncStackLog(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        # 方法信息
        #   方法 名   funcName
        #   方法 参数 parameters
        #   方法 行   line
        self.funcInfoList = []
        # 目标路径缓存
        self.srcFolderPath = None

    def create(self):
        super(LuaFuncStackLog, self).create()

    def destory(self):
        super(LuaFuncStackLog, self).destory()

    def addFuncStackLogFolder(self, srcFolderPath_: str, targetFolderPath_: str):
        self.srcFolderPath = srcFolderPath_
        folderUtils.convertFolderFiles(self.addFuncStackLogFile, self.srcFolderPath, targetFolderPath_, [".lua"])

    def addFuncStackLogFile(self, filePath_: str):
        _lines = fileUtils.linesFromFile(filePath_)
        _shortFilePath = filePath_.split(self.srcFolderPath).pop()
        _newLines = ["require \"LogUtils\"\n"]
        for _line in _lines:
            _funcInfo = {}
            # a.b = function(c)
            _funcReg = re.search(r'^\s*([A-Za-z0-9_\.]+)\s*=\s*function\s*\((.*)\)\s*', _line)
            if not _funcReg:
                # function a:b(c) / function a.b(c) / function a(c)
                _funcReg = re.search(r'^\s*function\s+([A-Za-z0-9_\:\.]+)\s*\((.*)\)\s*', _line)
                if not _funcReg:
                    # local a function(c)
                    _funcReg = re.search(r'^\s*local\s+([0-9a-zA-Z_]+)\s+function\s*\((.*)\)\s*', _line)
                    if not _funcReg:
                        # local a = function(c)
                        _funcReg = re.search(r'^\s*local\s+([A-Za-z0-9_]+)\s*=\s*function\s*\((.*)\)\s*', _line)
                        if not _funcReg:
                            # local function a(c)
                            _funcReg = re.search(r'^\s*local\s+function\s+([0-9a-zA-Z_]+)\s*\((.*)\)\s*', _line)
            if _funcReg:  # 有名函数
                # _funcInfo["funcName"] = _funcReg.group(1)
                # _funcInfo["parameters"] = _funcReg.group(2)
                # _funcInfo["line"] = _line
                # self.funcInfoList.append(_funcInfo)
                _newLines.append(
                    _line.replace(
                        _funcReg.group(0),
                        _funcReg.group(0) + \
                        "LogUtils.funcIn(\"" + _shortFilePath + "\",\"" + _funcReg.group(1) + "\")\n"
                    )
                )
            else:
                _funcReg = re.search(r'\bfunction\s*\((.*)\)$', _line)
                if _funcReg:  # 匿名函数
                    # _funcInfo["funcName"] = None
                    # _funcInfo["parameters"] = _funcReg.group(1)
                    # _funcInfo["line"] = _line
                    # self.funcInfoList.append(_funcInfo)
                    _newLines.append(
                        _line.replace(
                            _funcReg.group(0),
                            _funcReg.group(0) + \
                            "LogUtils.funcIn(\"" + _shortFilePath + "\",nil)\n"
                        )
                    )
                else:
                    _newLines.append(_line)
        return "".join(_newLines)
