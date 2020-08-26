#!/usr/bin/env python3
# Created by jiasy at 2020/5/16
from base.supports.Base.BaseInService import BaseInService
from utils import *
import re


class AdjustDelegate(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(AdjustDelegate, self).create()

    def destory(self):
        super(AdjustDelegate, self).destory()

    # 整理 delegate 的书写格式
    def adjustDelegateFolder(self, srcFolderPath_: str, targetFolderPath_: str):
        _csCodeFolder = fileUtils.getPath(srcFolderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        for _path in _filePathList:
            print(_path)
            _content = self.adjustDelegateFile(_path)
            _targetFilePath = targetFolderPath_ + _path.split(srcFolderPath_).pop()
            fileUtils.writeFileWithStr(_targetFilePath, _content)

    def adjustDelegateFile(self, filePath_: str):
        _content = fileUtils.readFromFile(filePath_)
        self.funcThreePartSeparate(_content)
        return _content

    def getContentFromLines(self, lines_: list, startLineIdx_, startCharIdx_, endLineIdx_, endCharIdx_):
        if startLineIdx_ == endLineIdx_:
            _line = lines_[startLineIdx_]
            return _line[startCharIdx_:endCharIdx_ - 1]
        else:
            _content = ""
            _content += lines_[startLineIdx_][startCharIdx_:len(lines_[startLineIdx_])]
            for _idx in range(startLineIdx_ + 1, endLineIdx_):
                _content += lines_[_idx]
            _content += lines_[endLineIdx_][0:endCharIdx_ - 1]
            return _content

    # 获取方法，然后将其分成三段
    def funcThreePartSeparate(self, content_: str):
        _pairList = [
            ["delegate(", ["){"]],
            ["(", [")=>{", ")"]],
            ["{", ["}"]]
        ]
        _singleQuotes: bool = False  # 单双引号
        _doubleQuotes: bool = False
        _specialQuotes: bool = False  # @" 起始，" 结束 之间
        _lines = content_.split("\n")
        _lineIdx = 0
        _length = len(_lines)
        _stackList = []
        while _lineIdx < _length:
            _line = _lines[_lineIdx]
            if not _line.lstrip().startswith("#"):
                _charLength = len(_line)
                _charIdx = 0
                while _charIdx < _charLength:  # 挨个字符遍历
                    _char = _line[_charIdx]
                    if not _doubleQuotes and not _singleQuotes and not _specialQuotes:
                        # 双引号起始的话，寻找结束
                        if _char == '"':
                            _doubleQuotes = True
                            _charIdx = _charIdx + 1
                            continue
                        # 单引号起始的话，寻找结束
                        if _char == "'":
                            _singleQuotes = True
                            _charIdx = _charIdx + 1
                            continue
                        # 特殊引号
                        _resultTuple = strUtils.checkStr(_line, _charIdx, '@"')
                        if _resultTuple[0]:
                            _specialQuotes = True
                            _charIdx = _resultTuple[1]
                            continue

                        _matchBoo = False
                        # 查找匹配对儿,找到键进行压栈
                        for _pair in _pairList:
                            _pairKey = _pair[0]
                            _pairValueList = _pair[1]
                            if len(_pairKey) == 1:
                                if _char == _pairKey:
                                    _charIdx = _charIdx + 1
                                    _stackList.append(
                                        {"key": _pairKey,
                                         "valueList": _pairValueList,
                                         "startLineIdx": _lineIdx,
                                         "startCharIdx": _charIdx}
                                    )
                                    _matchBoo = True
                                    break
                            else:
                                _resultTuple = strUtils.checkStr(_line, _charIdx, _pairKey)
                                if _resultTuple[0]:
                                    _charIdx = _resultTuple[1]
                                    _stackList.append(
                                        {"key": _pairKey,
                                         "valueList": _pairValueList,
                                         "startLineIdx": _lineIdx,
                                         "startCharIdx": _charIdx}
                                    )
                                    _matchBoo = True
                                    break
                        if _matchBoo:
                            continue

                        # 键值封闭区间判断
                        if len(_stackList) > 0:  # 有堆栈的话，判断最后一个是否结束
                            _stack = _stackList[-1]
                            _valueList = _stack["valueList"]
                            _stackResult = None
                            for _value in _valueList:
                                if len(_value) == 1:
                                    if _char == _value:
                                        _charIdx = _charIdx + 1
                                        _stackList.pop()
                                        _stackResult = _stack
                                        _stackResult["keyValue"] = _stack["key"] + _value
                                        break
                                else:
                                    _resultTuple = strUtils.checkStr(_line, _charIdx, _value)
                                    if _resultTuple[0]:
                                        _charIdx = _charIdx + 1
                                        _stackList.pop()
                                        _stackResult = _stack
                                        _stackResult["keyValue"] = _stack["key"] + _value
                                        break
                            # 有keyValue封闭
                            if not _stackResult == None:
                                _needPrint = False
                                if _stackResult["keyValue"] == "delegate(){":
                                    print(_stackResult["keyValue"] + " : ")
                                    _needPrint = True
                                elif _stackResult["keyValue"] == "()=>{":
                                    print(_stackResult["keyValue"] + " : ")
                                    _needPrint = True
                                if _needPrint:
                                    _startLineIdx = _stackResult["startLineIdx"]
                                    _startCharIdx = _stackResult["startCharIdx"]
                                    print(
                                        self.getContentFromLines(
                                            _lines,
                                            _startLineIdx,
                                            _startCharIdx,
                                            _lineIdx,
                                            _charIdx
                                        )
                                    )
                                continue
                    else:
                        if _doubleQuotes or _singleQuotes:
                            if _char == '\\' and _charIdx < (_length - 1):  # 转意字符
                                _charIdx = _charIdx + 2
                                continue
                            else:
                                if _doubleQuotes:
                                    if _char == '"':
                                        _doubleQuotes = False
                                if _singleQuotes:
                                    if _char == "'":
                                        _singleQuotes = False
                        if _specialQuotes:
                            if _char == '"':
                                _specialQuotes = False
                    _charIdx = _charIdx + 1

                # _stackStr = ""
                # for _stack in _stackList:
                #     _stackStr += "," + _stack["key"]
                # if len(_stackList) == 0:
                #     _stackStr = "x"
                # print(str(_lineIdx) + " : " + _line + "\n" + _stackStr)

            _lineIdx = _lineIdx + 1
