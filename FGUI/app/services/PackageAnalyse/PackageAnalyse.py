#!/usr/bin/env python3

from base.supports.Service.BaseService import BaseService
from utils import xmlUtils


class PackageAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(PackageAnalyse, self).create()
        # 解析给定目录
        self.analysePackage('/Volumes/18604037792/develop/ShunYuan/FGUI/Pyramid/assets/')

    def destory(self):
        super(PackageAnalyse, self).destory()

    def analysePackage(self, packagePath_: str):
        _xmlPathToJsonContentDict = xmlUtils.xmlToJsonDictInFolder(packagePath_)
        for _xmlPath in _xmlPathToJsonContentDict:
            _jsonContent = _xmlPathToJsonContentDict[_xmlPath]
            print(str(_xmlPath))
