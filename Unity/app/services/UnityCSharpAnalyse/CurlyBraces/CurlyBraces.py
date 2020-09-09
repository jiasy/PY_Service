#!/usr/bin/env python3
# Created by jiasy at 2020/5/15
from base.supports.Base.BaseInService import BaseInService
from utils import fileUtils
from utils import folderUtils
from utils import strUtils
from typing import Callable


class CSharpCurlyBracesFileObject(object):
    # 内存中创建成功
    def __init__(self):
        self.curlyBracesCount: int = 0
        self.debugBool = False

    def checkCulyBracesFolder(self, folderPath_: str):
        _csCodeFolder = fileUtils.getPath(folderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        _shortFilePathList = []
        for _path in _filePathList:
            if not self.checkCulyBracesFile(_path):
                _shortFilePathList.append(_path.split(folderPath_).pop())
        return _shortFilePathList

    def checkCulyBracesFile(self, filePath_: str):
        _lines = fileUtils.linesFromFile(filePath_)
        self.analyCurlyBraces(_lines)
        if self.curlyBracesCount != 0:
            return False
        else:
            return True

    def analyCurlyBraces(self, lines_: list):
        _lines = lines_[0:len(lines_)]
        self.walkLines(_lines, 0, 0, self.charPairCurlyBraces)

    def analyCurlyBracesPart(self, lines_: list, startLineIdx_: int, endLineIdx_: int):
        _lines = lines_[startLineIdx_:endLineIdx_ + 1]
        self.walkLines(_lines, 0, 0, self.charPairCurlyBraces)

    # 找闭合大括号
    def getCloseCurlyBraces(self, lines_: list, startLineIdx_: int, startCharIdx_: int = 0):
        _lineAndCharIdx = self.walkLines(lines_, startLineIdx_, startCharIdx_, self.charCloseCurlyBraces)
        return (_lineAndCharIdx[0], _lineAndCharIdx[1])

    # 对不是字符串内的字符进行逐个处理
    def walkLines(self,
                  lines_: list,
                  startLineIdx_: int,
                  startCharIdx_: int,
                  charFunc: Callable[[str, int, int], bool]
                  ):
        self.curlyBracesCount = 0  # 重置行的大括号计数
        _singleQuotes: bool = False  # 单双引号
        _doubleQuotes: bool = False
        _specialQuotes: bool = False  # @" 起始，" 结束 之间
        _linesLength = len(lines_)
        _currentLineIdx = startLineIdx_
        while _currentLineIdx < _linesLength:
            _line = lines_[_currentLineIdx]
            # 不是一个宏，才解析
            if not _line.lstrip().startswith("#"):
                # 挨个字符遍历
                _charIdx = 0
                if _currentLineIdx == startLineIdx_:
                    _charIdx = startCharIdx_
                _length = len(_line)
                while _charIdx < _length:
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

                        if charFunc(_char, _currentLineIdx, _charIdx):
                            # 返回第几行，第几个字符
                            return (_currentLineIdx, _charIdx)
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
            _currentLineIdx = _currentLineIdx + 1
            if self.debugBool:
                print(
                    str(_currentLineIdx + 1) + " " + _line + " -> " +
                    str(self.curlyBracesCount) + "\n" +
                    "_singleQuotes : " + str(_singleQuotes) + "\n" +
                    "_doubleQuotes : " + str(_doubleQuotes) + "\n" +
                    "_specialQuotes : " + str(_specialQuotes) + "\n"
                )
        return None

    # 当前的字符，第几行，第几个
    def charPairCurlyBraces(self, char_: str, lineIdx_: int, charIdx_: int):
        if char_ == "{":
            self.curlyBracesCount = self.curlyBracesCount + 1
        elif char_ == "}":
            self.curlyBracesCount = self.curlyBracesCount - 1
        return False  # 无论如何都不结束

    #
    def charCloseCurlyBraces(self, char_: str, lineIdx_: int, charIdx_: int):
        if char_ == "{":
            self.curlyBracesCount = self.curlyBracesCount + 1
        elif char_ == "}":
            self.curlyBracesCount = self.curlyBracesCount - 1

        if self.curlyBracesCount < 0:
            return True  # 非自我闭合退出循环
        else:
            return False  # 自我闭合，不退出循环


class CurlyBraces(BaseInService):
    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.cSharpCurlyBracesFileObject = CSharpCurlyBracesFileObject()

    def create(self):
        super(CurlyBraces, self).create()

    def destory(self):
        super(CurlyBraces, self).destory()

    # 从那一行开始，在行中找到第一个不匹配的括号
    def getCloseCurlyBraces(self, startIdx_: int, lines_: list):
        return self.cSharpCurlyBracesFileObject.getCloseCurlyBraces(lines_, startIdx_)
