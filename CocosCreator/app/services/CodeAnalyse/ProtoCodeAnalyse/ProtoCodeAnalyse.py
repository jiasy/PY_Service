#!/usr/bin/env python3
# Created by jiasy at 2020/4/21
from base.supports.Base.BaseInService import BaseInService
from utils import *
import re


# 分析代码，获取使用proto的文件，并整理成json结构。
class ProtoCodeAnalyse(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self._jsFolder = "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/scripts/"
        self._protoCalledList = []  # 被代码调用的proto
        self._jsNameFilterList = [
            "protocal.js",
            "message.sender.js",
            "message.handler.js"
        ]
        self._jsCodeFilterList = [
            "protocal.init(",
            "protocal.decodeMessage(",
            "protocal.encodeMessage("
        ]

        # 识别出监听，发送，注销，其他类型的proto调用
        self._sendLines = []
        self._onLines = []
        self._offLines = []
        self._otherLines = []

        # 识别出各类型的proto名称
        self._sendProtoNameList = []
        self._onProtoNameList = []
        self._offProtoNameList = []
        self._otherProtoNameList = []
        self._allProtoNameList = []

        self._jsProtoRelationDict = {}

    def create(self):
        super(ProtoCodeAnalyse, self).create()

    def destory(self):
        super(ProtoCodeAnalyse, self).destory()

    def analyse(self):
        _filePathDict = folderUtils.getFilePathKeyValue(self._jsFolder, [".js"])
        for _fileName, _filePath in _filePathDict.items():
            if _fileName in self._jsNameFilterList:
                continue
            self.analyseJS(_filePath)

        # 冲解析出来的协议行中获取信息
        for _line in self._sendLines:
            _sendResult = re.search(r'.*\(protocal\.([0-9a-z-A-Z_]+)', _line)
            _protoName = _sendResult.group(1)
            if not (_protoName in self._sendProtoNameList):
                self._sendProtoNameList.append(_protoName)
            if not (_protoName in self._allProtoNameList):
                self._allProtoNameList.append(_protoName)

        for _line in self._onLines:
            _sendResult = re.search(r'.*\(protocal\.([0-9a-z-A-Z_]+)', _line)
            _protoName = _sendResult.group(1)
            if not (_protoName in self._onProtoNameList):
                self._onProtoNameList.append(_protoName)
            if not (_protoName in self._allProtoNameList):
                self._allProtoNameList.append(_protoName)

        for _line in self._offLines:
            _sendResult = re.search(r'.*\(protocal\.([0-9a-z-A-Z_]+)', _line)
            _protoName = _sendResult.group(1)
            if not (_protoName in self._offProtoNameList):
                self._offProtoNameList.append(_protoName)
            if not (_protoName in self._allProtoNameList):
                self._allProtoNameList.append(_protoName)

        matches = re.finditer(r'protocal\.([0-9a-z-A-Z_]+)', "\n".join(self._otherLines), re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                _protoName = match.group(groupNum)
                if not (_protoName in self._otherProtoNameList) and \
                        not (_protoName in self._sendProtoNameList) and \
                        not (_protoName in self._onProtoNameList) and \
                        not (_protoName in self._offProtoNameList):
                    self._otherProtoNameList.append(_protoName)
                if not (_protoName in self._allProtoNameList):
                    self._allProtoNameList.append(_protoName)

        print("other --------")
        for _protoName in self._otherProtoNameList:
            print("    " + _protoName)

        print("send --------")
        for _protoName in self._sendProtoNameList:
            print("    " + _protoName)

        # print("on --------")
        # for _protoName in self._onProtoNameList:
        #     print("    " + _protoName)
        #
        # print("off --------")
        # for _protoName in self._offProtoNameList:
        #     print("    " + _protoName)

        print("on but not off --------")
        for _protoName in self._onProtoNameList:
            if not _protoName in self._offProtoNameList:
                print("    " + _protoName)

        print("on and off --------")
        for _protoName in self._onProtoNameList:
            if _protoName in self._offProtoNameList:
                print("    " + _protoName)

        print("all -----------")
        for _protoName in self._allProtoNameList:
            print("    " + _protoName)

    def analyseJS(self, jsPath_: str):
        _lines = fileUtils.linesFromFile(jsPath_)

        # 获取短名
        _jsShortName = jsPath_.split(self._jsFolder).pop()
        _send = []
        _on = []
        _off = []
        _onAndOff = []
        _onNotOff = []

        for _line in _lines:
            _isFindBoo = False
            for _codeFilter in self._jsCodeFilterList:
                if _line.find(_codeFilter) > 0:
                    _isFindBoo = True
                    continue
            if not _isFindBoo:
                # 去除注释行，识别特殊字符
                if _line.find("protocal.") > 0 and not _line.strip().startswith("//"):
                    _protoResult = re.search(r'.*\(protocal\.([0-9a-z-A-Z_]+)', _line)
                    if _protoResult:
                        _protoName = _protoResult.group(1)
                        _sendResult = re.search(r'.*send\s*\(\s*protocal\s*\.([0-9a-z-A-Z_]+)', _line)
                        if _sendResult:
                            self._sendLines.append(_line)
                            if not (_protoName in _send):
                                _send.append(_protoName)
                        else:
                            _onResult = re.search(r'.*on\s*\(\s*protocal\s*\.([0-9a-z-A-Z_]+)', _line)
                            if _onResult:
                                self._onLines.append(_line)
                                if not (_protoName in _on):
                                    _on.append(_protoName)
                            else:
                                _offResult = re.search(r'.*off\s*\(\s*protocal\s*\.([0-9a-z-A-Z_]+)', _line)
                                if _offResult:
                                    self._offLines.append(_line)
                                    if not (_protoName in _off):
                                        _off.append(_protoName)
                                else:
                                    self._otherLines.append(_line)
                    else:
                        self._otherLines.append(_line)

        # 挂载信息
        for _protoName in _on:
            if _protoName in _off:
                _onAndOff.append(_protoName)
            else:
                _onNotOff.append(_protoName)
        self._jsProtoRelationDict[_jsShortName] = {}
        self._jsProtoRelationDict[_jsShortName]["send"] = _send
        self._jsProtoRelationDict[_jsShortName]["on"] = _on
        self._jsProtoRelationDict[_jsShortName]["off"] = _off
        self._jsProtoRelationDict[_jsShortName]["onAndOff"] = _onAndOff
        self._jsProtoRelationDict[_jsShortName]["onNotOff"] = _onNotOff
