#!/usr/bin/env python3
# Created by jiasy at 2020/5/15
from base.supports.Base.BaseInService import BaseInService
from utils import folderUtils
from utils import fileUtils
from utils import strUtils
from utils import pyUtils
import re


class AdjustIfElse(BaseInService):
    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(AdjustIfElse, self).create()

    def destory(self):
        super(AdjustIfElse, self).destory()

    # 将一行if拆分开 将多行 } else { 合并-----------------------------------------------------------------
    def adjustIfElseFolder(self, srcFolderPath_: str, targetFolderPath_: str):
        _csCodeFolder = fileUtils.getPath(srcFolderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        for _path in _filePathList:
            print(_path)
            _content = self.adjustIfElseFile(_path)  # 拆分 单行 } else {
            _content = self.elseCombine(_content)  # 合并多行 } else {
            _targetFilePath = targetFolderPath_ + _path.split(srcFolderPath_).pop()
            fileUtils.writeFileWithStr(_targetFilePath, _content)

    # if () return
    # else if () return
    # else return

    def adjustIfElseReturn(self, content_):
        _content = content_
        _oneLineReg = r'^(.*)(if|else if)\s*\((.*)\)\s*return\s+(.*);$'
        matches = re.finditer(_oneLineReg, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            if not _prefix.strip() == "":
                self.raiseError(
                    pyUtils.getCurrentRunningFunctionName(),
                    "if/else if 和 return 成行，前缀必须是空白 : " + match.group(0)
                )
            _blank = _prefix
            _ifOrIfElse = match.group(2)
            _ifContent = match.group(3)
            _returnContent = match.group(4)
            _targetCode = _blank + _ifOrIfElse + "(" + _ifContent + "){" + "\n"
            _targetCode += _blank + "    return " + _returnContent + ";" + "\n"
            _targetCode += _blank + "}"
            _content = _content.replace(match.group(0), _targetCode)
        _oneLineReg = r'^(.*)else\s*return\s+(.*);$'
        matches = re.finditer(_oneLineReg, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            if not _prefix.strip() == "":
                # 不是 #else 这样的宏
                if not _prefix.startswith("#"):
                    self.raiseError(
                        pyUtils.getCurrentRunningFunctionName(),
                        "else 和 return 成行，前缀必须是空白 : " + match.group(0)
                    )
            else:
                _blank = _prefix
                _returnContent = match.group(2)
                _targetCode = _blank + "else{" + "\n"
                _targetCode += _blank + "    return " + _returnContent + ";" + "\n"
                _targetCode += _blank + "}"
                _content = _content.replace(match.group(0), _targetCode)

    def adjustIfElseFile(self, filePath_: str):
        _lines = fileUtils.linesFromFile(filePath_)
        _lineLength = len(_lines)
        _newLines = []
        # no 没找到，ing 正在，end 结束
        for _lineIdx in range(_lineLength):
            _line = _lines[_lineIdx]
            _line = _line.rstrip()
            _oneLineReg = re.search(r"^[\s\^\"^\']*if\s*\((.*\))(.*);$", _line)
            if _oneLineReg:
                _line = self.breakOneLineIf(_line)
            _newLines.append(_line)
        return "\n".join(_newLines)

    def breakOneLineIf(self, line_: str):
        _ifStartIdx = -1
        _ifEndIdx = -1
        _ifContentStartIdx = -1
        _ifContentEndIdx = -1
        _elseContentStartIdx = -1
        _elseContentEndIdx = -1
        # if的状态
        _ifState = "no"
        # 单双引号
        _singleQuotes: bool = False
        _doubleQuotes: bool = False
        # @" 起始，" 结束 之间
        _specialQuotes: bool = False
        _pairCount: int = 0
        _line = line_
        # 将 if( 格式统一
        _line = re.sub('if\s+\(', 'if(', _line)
        # 将 ;else 格式统一
        _line = re.sub(';\s*else\s+', ';else ', _line)
        # 挨个字符遍历
        _charIdx = 0
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

                if _char == "(":
                    _pairCount = _pairCount + 1
                elif _char == ")":
                    _pairCount = _pairCount - 1

                if _ifState == "no":  # 还没找到 if
                    _resultTuple = strUtils.checkStr(_line, _charIdx, 'if(')
                    if _resultTuple[0]:
                        _ifState = 'ing'  # 找到了
                        _charIdx = _resultTuple[1]
                        _ifStartIdx = _charIdx
                        continue
                elif _ifState == "ing":
                    if _pairCount < 0:  # 找到第一个没匹配的括号【认为if之前没有括号，所以，0就是正好匹配的位置】
                        _ifState = 'end'  # 那就是if的，
                        _pairCount = _pairCount + 1  # 和if(匹配的括号要加一个
                        _ifEndIdx = _charIdx
                        _ifContentStartIdx = _charIdx + 1
                        continue
                elif _ifState == 'end':
                    _resultTuple = strUtils.checkStr(_line, _charIdx, 'elif')
                    if _resultTuple[0]:
                        self.raiseError(pyUtils.getCurrentRunningFunctionName(), "elif 在同一行 : " + _line)

                    _resultTuple = strUtils.checkStr(_line, _charIdx, ';else ')
                    if _resultTuple[0]:
                        _ifState = 'else'  # 找到了
                        _ifContentEndIdx = _charIdx  # if 的内容结束
                        _charIdx = _resultTuple[1]
                        _elseContentStartIdx = _charIdx
                        _elseContentEndIdx = len(_line) - 1
                        break  # 不在循环，找到 else 内容的结尾，停止循环
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

        if _ifContentEndIdx == -1:  # 没有找到过if内容的结尾，就在最后结束。找到的情况是因为else
            _ifContentEndIdx = len(_line) - 1
        # print(str(_line))
        ifStr = _line[_ifStartIdx:_ifEndIdx]
        ifContent = _line[_ifContentStartIdx:_ifContentEndIdx].strip()
        elseContent = ""
        if _elseContentEndIdx > 0:
            elseContent = _line[_elseContentStartIdx:_elseContentEndIdx].strip()
        prefix = str(_line[0:_ifStartIdx - 3])
        # print(prefix + "   " + ifStr + "  " + ifContent + "      " + elseContent)

        newLine = ""
        if elseContent == "":
            newLine += prefix + "if(" + ifStr + "){" + "\n"
            newLine += prefix + "    " + ifContent + ";" + "\n"
            newLine += prefix + "}" + "\n"
        else:
            newLine += prefix + "if(" + ifStr + "){" + "\n"
            newLine += prefix + "    " + ifContent + ";" + "\n"
            newLine += prefix + "} else {" + "\n"
            newLine += prefix + "    " + elseContent + ";" + "\n"
            newLine += prefix + "}" + "\n"
        # print(newLine)
        return newLine

    def elseCombine(self, content_: str):
        _content = content_
        _elseReg = r'^(\s+)\}\s*else\s*\{'
        matches = re.finditer(_elseReg, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            _content = _content.replace(match.group(0), _prefix + "}else{")
        return _content
