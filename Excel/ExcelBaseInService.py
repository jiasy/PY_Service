#!/usr/bin/env python3
# Created by jiasy at 2020/9/10
from base.supports.Base.BaseInService import BaseInService
from utils import pyUtils


class ExcelBaseInService(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = None

    def create(self):
        super(ExcelBaseInService, self).create()

    def destory(self):
        super(ExcelBaseInService, self).destory()

    # 检验是否这个方法设定
    def checkFunction(self, sFunctionName_: str):
        if sFunctionName_ in self.funcDict:
            return True
        else:
            return False

    # 错误的时候，返回内容
    def checkParameters(self, sFunctionName_, dParameters_):
        _parameterInfoDict = self.funcDict[sFunctionName_]
        for _parameterName in _parameterInfoDict:
            if not _parameterName in dParameters_:
                return "缺少参数 " + _parameterName + "【" + _parameterInfoDict[_parameterName] + "】"
        return None

    def doExcelFunc(self, sFunctionName_: str, dParameters_: dict):
        if hasattr(self, sFunctionName_):  # 使用反射
            _function = getattr(self, sFunctionName_)
            _function(dParameters_)
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), " excel 不存在这个方法 : " + sFunctionName_)
