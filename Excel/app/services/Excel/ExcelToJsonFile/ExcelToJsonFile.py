#!/usr/bin/env python3
# Created by jiasy at 2020/9/7
from base.supports.Base.BaseInService import BaseInService
from utils import *


class ExcelToJsonFile(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(ExcelToJsonFile, self).create()

    def destory(self):
        super(ExcelToJsonFile, self).destory()

    def doExcelFunc(self, dParameters_: dict):
        dictUtils.showDictStructure(dParameters_)


import Main

if __name__ == "__main__":
    _baseServiceName = "Excel"
    _subBaseInServiceName = "ExcelToJsonFile"
    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 所需参数
            "sourceFolder": "{sResPath}/source",
            "targetFolder": "{sResPath}/target"
        },
        {  # 命令行进行的全局参数修改
            "publicType": "test"
        }
    )
