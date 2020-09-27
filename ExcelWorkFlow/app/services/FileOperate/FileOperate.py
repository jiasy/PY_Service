#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import fileUtils


class FileOperate(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(FileOperate, self).create()

    def destory(self):
        super(FileOperate, self).destory()

    # 移除每一行的前几个字符
    def removeFirstCharsInEveryLine(self, filePath_: str, charCount_: int):
        _lines = fileUtils.linesFromFile(filePath_)
        for _i in range(len(_lines)):
            _lines[_i] = _lines[_i][charCount_:]
        fileUtils.writeFileWithStr(filePath_, "".join(_lines))
        return
