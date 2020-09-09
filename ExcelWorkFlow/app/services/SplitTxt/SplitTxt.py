#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import fileUtils
import re


# 切割文本文件，成零散文件，用来切小说
class SplitTxt(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SplitTxt, self).create()
        txtName = "策略思维"
        self.txtFolderPath = "/Volumes/Files/课本/小说/"
        self.filePath = self.txtFolderPath + txtName
        self.targetFolderPath = self.filePath + "章节"
        # 移除空白行
        # self.removeBlankLine(self.filePath)
        # 拆分文件
        # self.splitFile(self.filePath)
        self.splitFileWordStartLine(self.filePath)

    def destory(self):
        super(SplitTxt, self).destory()

    def stripLine(self, filePath_: str):
        _tempLines = []
        _lines = fileUtils.linesFromFile(filePath_)
        for _i in range(len(_lines)):
            # 去掉没一行的左右空格
            _line = _lines[_i].strip()
            _tempLines.append(_line)
        fileUtils.writeFileWithStr(filePath_ + "_strip", "".join(_tempLines))

    def removeBlankLine(self, filePath_: str):
        _tempLines = []
        _lines = fileUtils.linesFromFile(filePath_)
        for _i in range(len(_lines)):
            _line = _lines[_i]
            # 去掉空白行
            if _line.strip() == "":
                continue
            else:
                _tempLines.append(_line)
        fileUtils.writeFileWithStr(filePath_ + "_noBlank", "".join(_tempLines))

    # 章节标题从头起，内容缩进
    def splitFileWordStartLine(self, filePath_: str):
        _lines = fileUtils.linesFromFile(filePath_)
        # 章节数
        _chapterCount = 0
        # 内容缓存
        _splitLines = []
        # 用于切分的正则
        _contentRegStr = r'^\s.*'
        for _i in range(len(_lines)):
            _line = _lines[_i]
            _contentReg = re.search(_contentRegStr, _line)
            if not _contentReg:
                _chapterCount = _chapterCount + 1
                # 将之前的内容形成一个章节文件
                self.linesToFileWordStartLine(self.targetFolderPath, _splitLines, _chapterCount)
                # 清空内容记录
                _splitLines = []
            # 将当前行放入内容记录
            _splitLines.append(_line)
        # 找到最后，最后一章的内容需要组合
        self.linesToFileWordStartLine(self.targetFolderPath, _splitLines, _chapterCount)

    def linesToFileWordStartLine(self, targetFolderPath_: str, lines_: list, chapterCount_: int):
        # 有内容，就形成文件
        if len(lines_) > 0:
            _splitFileContent = "".join(lines_)  # 拼接内容
            _splitFileName = str(chapterCount_).rjust(3) + "_" + lines_[0] + ".txt"  # 第一行做文件名
            fileUtils.writeFileWithStr(targetFolderPath_ + "/" + _splitFileName, _splitFileContent)

    def splitFile(self, filePath_: str):
        _lines = fileUtils.linesFromFile(filePath_)

        # 章节数
        _chapterCount = 0
        # 内容缓存
        _splitLines = []
        # 用于切分的正则
        # _titleRegStr = r'^\s*第([零一两俩二三四五六七八九十百千]*?)章 (.*)'
        _titleRegStr = r'^第(.*)章'
        for _i in range(len(_lines)):
            _line = _lines[_i]
            # 找到标题，整合上一章
            _titleReg = re.search(_titleRegStr, _line)
            if _titleReg:
                _nextLine = _lines[_i + 1]  # 连续两行都是章节名，那么就去掉下一行
                if re.search(_titleRegStr, _nextLine):
                    _lines[_i + 1] = ""
                _chapterCount = _chapterCount + 1
                # 将之前的内容形成一个章节文件
                self.linesToFile(self.targetFolderPath, _splitLines, _chapterCount)
                # 清空内容记录
                _splitLines = []

            # 将当前行放入内容记录
            _splitLines.append(_line)
        # 找到最后，最后一章的内容需要组合
        self.linesToFile(self.targetFolderPath, _splitLines, _chapterCount)

    def linesToFile(self, targetFolderPath_: str, lines_: list, chapterCount_: int):
        # 有内容，就形成文件
        if len(lines_) > 0:
            _splitFileContent = "".join(lines_)  # 拼接内容
            _splitFileName = str(chapterCount_).rjust(3) + "_" + lines_[0] + ".txt"  # 第一行做文件名
            fileUtils.writeFileWithStr(targetFolderPath_ + "/" + _splitFileName, _splitFileContent)
