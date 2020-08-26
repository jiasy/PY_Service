#!/usr/bin/env python3
# Created by jiasy at 2020/6/3
from base.supports.Base.BaseInService import BaseInService
from utils import *
import os
import subprocess


class PbCreator(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(PbCreator, self).create()

    def destory(self):
        super(PbCreator, self).destory()

    def createPbFile(self, protoFolderPath_: str, pbCreateFolderPath_: str):
        _filePathDict = folderUtils.getFilePathKeyValue(protoFolderPath_, [".proto"])
        for _protoName, _protoPath in _filePathDict.items():
            _protoShortPath = _protoPath.split(protoFolderPath_)[1]
            _pbShortPath = _protoShortPath.split(".proto")[0] + ".pb"
            _cmd = "protoc --descriptor_set_out ./{0} ./{1}".format(_pbShortPath, _protoShortPath)
            print('_cmd = ' + str(_cmd))
            subprocess.Popen(_cmd, shell=True, cwd=protoFolderPath_)

        fileCopyUtils.copyFilesInFolderTo([".pb"], protoFolderPath_, pbCreateFolderPath_, "include", True)
        folderUtils.removeFileByFilter(protoFolderPath_, [".pb"])
