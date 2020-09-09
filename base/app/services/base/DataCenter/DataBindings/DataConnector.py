#!/usr/bin/env python3
from base.app.services.base.DataCenter.DataBindings.DataBase import DataBase
from utils import pyUtils


class DataConnector(DataBase):
    def __init__(self, sm_):
        super().__init__(sm_)
        self.finalValue: str = None

    def create(self):
        super(DataConnector, self).create()

    def destory(self):
        super(DataConnector, self).destory()

    def resetDataPath(self, dataPath_: str):
        super(DataConnector, self).resetDataPath(dataPath_)
        _dataStr: str = self.getValue(self.dataPath)
        self.resetByStr(_dataStr)

    def recreateListeners(self, dataStr_: str):
        self.removeDataPathListeners()
        self.splitDataStr(dataStr_)
        _length: int = len(self.dataPathListenerList)
        for i in range(_length):
            self.dataEventMgr.registerEvent(self.dataPathListenerList[i], self)

    # 返回一个二元组，(是否成功，数据变化之后重新计算的结果)
    def dataChanged(self):
        _final_string: str = ""
        if self.dataPathListenerList is None:
            return False, None
        _length: int = len(self.dataPathListenerList)
        for i in range(_length):
            _dataStr = self.dc.gv(self.dataPathListenerList[i])
            if _dataStr is None:
                self.raiseError(pyUtils.getCurrentRunningFunctionName(), self.dataPathListenerList[i] + " 值为空")
                return False, None
            _final_string = _final_string + self.otherStringList[i] + str(_dataStr)
        _final_string = _final_string + self.otherStringList[-1]
        self.finalValue = _final_string
        # # 没有绑定的显示对象
        # if self.displayObject:
        # # 显示文本变更
        # else:
        #     if self.dataPath:
        #         print(self.dataPath + " : " + self.finalValue)
        #     else:
        #         print(self.dataStr + " : " + self.finalValue)
        return True, self.finalValue
