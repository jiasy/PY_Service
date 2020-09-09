#!/usr/bin/env python3
from base.supports.Base.BaseInService import BaseInService
from utils import folderUtils
from utils import fileUtils
from utils import strUtils
from utils import pyUtils
import re


class LuaRemoveComment(BaseInService):
    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(LuaRemoveComment, self).create()

    def destory(self):
        super(LuaRemoveComment, self).destory()

    # 移除文件夹内的注释
    def luaRemoveCommentInFolder(self, srcFolderPath_: str, targetFolderPath_: str):
        folderUtils.convertFolderFiles(self.luaRemoveComment, srcFolderPath_, targetFolderPath_, [".lua"])

    def luaRemoveComment(self, filePath_: str):
        _lines = fileUtils.linesFromFile(filePath_)
        _singleQuotes: bool = False  # 单双引号
        _doubleQuotes: bool = False
        _specialQuotes: bool = False  # 特殊引号 [[ 起始，]] 结束 之间
        _commentLines: bool = False  # 多行注释 --[[ 起始，--]] 结束 之间
        _newLines = []  # 新行
        _lineNum = 0
        for _line in _lines:
            _line = _line.rstrip()  # 右侧空格无用
            _lineNum = _lineNum + 1
            if _commentLines:  # 多行注释中
                _multipleLineReg = re.search(r'(.*?\]\])', _line)  # 当前行是不是多行注释的结尾
                if not _multipleLineReg:
                    # 找不到多行注释的结尾，就直接越到下一行，当前行直接删除
                    # print(str(_lineNum) + " : ")  # + " -> " + str(_doubleQuotes)
                    _newLines.append("")  # 舍弃当前行
                    continue
            else:
                # 同一行内的多行注释去掉/*...*/，这样剩下的就是纯多行注释了
                regex = r'(\-\-\[\[.*?\]\])'
                matches = re.finditer(regex, _line, re.MULTILINE)
                for matchNum, match in enumerate(matches, start=1):
                    _line = _line.replace(match.group(1), "")

            # 挨个字符遍历
            _charIdx = 0
            _length = len(_line)
            while _charIdx < _length:
                if _charIdx >= len(_line):
                    self.raiseError(pyUtils.getCurrentRunningFunctionName(), "解析格式错误")
                _char = _line[_charIdx]
                # if _lineNum == 147 and _charIdx == 28:
                #     print("x")
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
                    _resultTuple = strUtils.checkStr(_line, _charIdx, '[[')
                    if _resultTuple[0]:
                        _specialQuotes = True
                        _charIdx = _resultTuple[1]
                        continue

                    # 不在注释中的话
                    if not _commentLines:
                        _resultTuple = strUtils.checkStr(_line, _charIdx, '--[[')
                        if _resultTuple[0]:
                            _commentLines = True  # --[[
                            _line = _line[0:_charIdx]  # 当前行已经完犊子，因为，之前已经去掉了同一行结束的多行注释。
                            break
                        else:
                            _resultTuple = strUtils.checkStr(_line, _charIdx, '--')
                            if _resultTuple[0]:
                                _line = _line[0:_charIdx]  # 当前行已经完犊子了
                                break

                    else:
                        # 多行注释中的话
                        _resultTuple = strUtils.checkStr(_line, _charIdx, "]]")
                        if _resultTuple[0]:
                            _charIdx = _resultTuple[1]  # 向下推荐一个字符
                            _line = _line[_charIdx: _length]  # 变更总长
                            _length = _length - _charIdx - 1  # 前面的都删了，剩余多少个字符
                            _charIdx = 0  # 变更当前序号，下一个循环从头开始
                            _commentLines = False
                            _charIdx = _charIdx + 1
                            continue  # 下一个字符
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
                        _resultTuple = strUtils.checkStr(_line, _charIdx, "]]")
                        if _resultTuple[0]:
                            _specialQuotes = False
                            _charIdx = _resultTuple[1]
                            continue
                _charIdx = _charIdx + 1
            # print(str(_lineNum) + " : " + _line.rstrip() + " -> " +
            #       str(_doubleQuotes) + "," +
            #       str(_singleQuotes) + "," +
            #       str(_specialQuotes)
            #       )
            _newLines.append(_line.rstrip())  # 右侧空格无用
        return "\n".join(_newLines)
