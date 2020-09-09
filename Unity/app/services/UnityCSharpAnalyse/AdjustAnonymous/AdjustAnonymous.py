#!/usr/bin/env python3
# Created by jiasy at 2020/5/16
from base.supports.Base.BaseInService import BaseInService
from utils import fileUtils
from utils import folderUtils
import re


class AdjustAnonymous(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(AdjustAnonymous, self).create()

    def destory(self):
        super(AdjustAnonymous, self).destory()

    # 整理 delegate 的书写格式
    def adjuseAnonymousFolder(self, srcFolderPath_: str, targetFolderPath_: str):
        _csCodeFolder = fileUtils.getPath(srcFolderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        for _path in _filePathList:
            print(_path)
            _content = self.adjuseAnonymousFile(_path)
            _targetFilePath = targetFolderPath_ + _path.split(srcFolderPath_).pop()
            fileUtils.writeFileWithStr(_targetFilePath, _content)

    def adjuseAnonymousFile(self, filePath_: str):
        _content = fileUtils.readFromFile(filePath_)
        _content = self.adjuseAnonymousWrite(_content)
        return _content

    # 调整一些基本写法
    def adjuseAnonymousWrite(self, content_: str):
        _content = content_
        # 没有参数的 ) => { ->  )=>{
        _content = re.sub(r'\)\s*=>\s*\{', ')=>{', _content)
        return _content
