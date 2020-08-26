#!/usr/bin/env python3
from base.supports.Base.BaseInService import BaseInService
from utils import pyUtils
from base.app.services.base.DataCenter.DataBindings.DataBase import DataBase
from typing import List
from base.supports.Base.Base import Base


class DataEventMgr(Base):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.dataEventDict = dict({})

    def create(self):
        super(DataEventMgr, self).create()

    def destory(self):
        super(DataEventMgr, self).destory()

    def registerEvent(self, dataPath_: str, baseBinding_: DataBase):
        if not (dataPath_ in self.dataEventDict):
            self.dataEventDict[dataPath_] = []
            self.dataEventDict[dataPath_].append(baseBinding_)

    def removeEvent(self, dataPath_: str, baseBinding_: DataBase):
        if dataPath_ in self.dataEventDict:
            _dataBases: List[DataBase] = self.dataEventDict[dataPath_]
            if baseBinding_ in _dataBases:
                list(_dataBases).remove(baseBinding_)
                baseBinding_.destory()
            if len(_dataBases) == 0:
                del self.dataEventDict[dataPath_]

    def hasDataShowerForDataPath(self, dataPath_: str):
        if dataPath_ in self.dataEventDict:
            return True
        else:
            return False

    def onDataChange(self, dataPath_: str):
        _value = self.sm.dc.gv(dataPath_)
        if isinstance(_value, str):
            # print('dataPath_ : ' + dataPath_ + " : " + _value)
            if dataPath_ in self.dataEventDict:
                _dataBases: List[DataBase] = self.dataEventDict[dataPath_]
                if _dataBases and len(_dataBases) > 0:
                    for _i in range(len(_dataBases)):
                        _dataBases[_i].dataChanged()
        else:
            if isinstance(_value, list):
                self.raiseError(pyUtils.getCurrentRunningFunctionName(), "<" + str(dataPath_) + "> 转换过后不能可有数组")
