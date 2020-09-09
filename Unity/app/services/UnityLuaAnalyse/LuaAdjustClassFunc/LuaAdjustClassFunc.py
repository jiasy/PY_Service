#!/usr/bin/env python3
# Created by jiasy at 2020/5/20
from base.supports.Base.BaseInService import BaseInService
from utils import folderUtils
from utils import fileUtils
import re


class LuaAdjustClassFunc(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        # 错误信息缓存
        self.errorDict = {}
        # 目标路径缓存
        self.srcFolderPath = None

    def create(self):
        super(LuaAdjustClassFunc, self).create()

    def destory(self):
        super(LuaAdjustClassFunc, self).destory()

    def getErrorInfo(self):
        _hasError = False
        for (_shortFilePath, _infoList) in self.errorDict.items():
            _hasError = True
            print(_shortFilePath)
            for _info in _infoList:
                print("    " + _info["desc"])
                print("        " + _info["line"])
        return _hasError

    def checkLuaStyle(self, srcFolderPath_: str):
        self.srcFolderPath = srcFolderPath_

        # 先校验 双function 和 双 end
        folderUtils.doFunForeachFileInFolder(self.doubleFuncOrEndInOneLine, srcFolderPath_, [".lua"])
        if self.getErrorInfo():  # 如果有非法格式
            return

        # 再检查 一行内的 开始 和 结束
        folderUtils.doFunForeachFileInFolder(self.funcAndEndInOneLine, srcFolderPath_, [".lua"])
        if self.getErrorInfo():  # 如果有非法格式
            return

    def doubleFuncOrEndInOneLine(self, path_: str):
        _lines = fileUtils.linesFromFile(path_)
        _errorList = []  # 问题列表
        for _line in _lines:
            # 一行内有两个function。。。
            _twoFunRegInLine = re.search(r'\bfunction\b.*\bfunction\b', _line)
            if _twoFunRegInLine:
                _errorList.append({
                    "desc": "同一行内有两个 function",
                    "line": _line
                })
            # 一行内是否有两个end
            _twoEndRegInLine = re.search(r'\bend\b.*\bend\b', _line)
            if _twoEndRegInLine:
                _errorList.append({
                    "desc": "同一行内有两个 end",
                    "line": _line
                })
        # 错误长度不为零，就记录到错误总汇
        if len(_errorList) > 0:
            self.errorDict[path_.split(self.srcFolderPath).pop()] = _errorList

    def funcAndEndInOneLine(self, path_: str):
        _lines = fileUtils.linesFromFile(path_)
        _errorList = []  # 问题列表
        for _line in _lines:
            # 一行内有两个function。。。
            _funcAndEndReg = re.search(r'\bfunction\b.*\bend\b', _line)
            if _funcAndEndReg:
                _errorList.append({
                    "desc": "同一行内有function ... end",
                    "line": _line
                })
        # 错误长度不为零，就记录到错误总汇
        if len(_errorList) > 0:
            self.errorDict[path_.split(self.srcFolderPath).pop()] = _errorList
