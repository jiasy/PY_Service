#!/usr/bin/env python3
from base.supports.Base.Base import Base
from typing import List
from utils import pyUtils
from utils import listUtils
from utils import disUtils


class DataBase(Base):
    def __init__(self, sm_):
        super().__init__(sm_)
        self.dc = self.sm.dc
        self.dataEventMgr = self.dc.dataEventMgr
        # 字符串拼路径
        self.dataPath: str = None
        # 当前数据转换结束后，拼接得到的文字
        self.dataStr: str = None
        # 如果是一个显示对象绑定的数据，它当前对应的显示对象
        self.displayObject: object = None
        # 监听的数据路径集合
        self.dataPathListenerList: List[str] = None
        # 用来拼接的其他字符串缓存
        self.otherStringList: List[str] = None

    def create(self):
        super(DataBase, self).create()

    def destory(self):
        super(DataBase, self).destory()

    # 返回一个二元组，(是否成功，数据变化之后重新计算的结果)
    def dataChanged(self):
        self.raiseError(pyUtils.getCurrentRunningFunctionName(), "needs override")

    # 根据字符串，或者路径，重新设置监听的数据路径。
    def recreateListeners(self, dataStr_: str):
        self.raiseError(pyUtils.getCurrentRunningFunctionName(), "needs override")

    # 重置数据路径，重新取值
    def resetDataPath(self, dataPath_: str):
        self.dataPath = dataPath_

    # 按照字符串，来重置数据监听
    def resetByStr(self, dataStr_: str):
        if not self.dataStr == dataStr_:
            # 字符串为新，才重构自身属性
            self.recreateListeners(dataStr_)
            self.dataStr = dataStr_
        return self.dataChanged()

    # 在数据路径是this.开头的时候，要转换成实际的数据空间
    def changeDataPath(self, dataPath_: str):
        _dataPath: str = dataPath_
        if _dataPath.find("this.") == 0:
            if not self.displayObject:
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                "ERROR : DataBase " + _dataPath + " 为UI数据路径，没有绑定是哪个UI")
                return None
            else:
                # 通过自己绑定的显示对象，获取，显示对象所处的数据路径
                _disPath = disUtils.getDisPath(self.displayObject)
                _dataPath = _disPath + "." + _dataPath.split("this.")[1]
        return _dataPath

    # 字符串拆分成数据部分，字符串部分
    def splitDataStr(self, dataString_: str):
        self.dataPathListenerList = []
        self.otherStringList = []
        if dataString_ and dataString_.find("${") >= 0:
            _dataPathListSplit: List[str] = dataString_.split("${")
            self.otherStringList.append(listUtils.list_shift(_dataPathListSplit))
            _length: int = len(_dataPathListSplit)
            for _idx in range(_length):
                _string_item: str = _dataPathListSplit[_idx]
                _string_list: List[str] = _string_item.split("}")
                self.dataPathListenerList.append(_string_list[0])
                self.otherStringList.append(_string_list[1])
        else:
            self.dataPathListenerList.append(self.dataPath)
            self.otherStringList.append("")
            self.otherStringList.append("")

    # 字符串，是不是一个数据路径
    def isDataPath(self, valueStr_: str):
        if valueStr_.find(".") > 0:
            return True
        else:
            return False

    # 通过字符串，获取值[路径 转换成 值] [值 就是 值]
    def getRealValue(self, dataPathStr_: str):
        if self.isDataPath(dataPathStr_):
            return self.getValue(dataPathStr_)
        else:
            return dataPathStr_

    def getValue(self, dataPathStr_: str):
        # 转换一下路径中的 this，变更成真正的路径
        _dataPath: str = self.changeDataPath(dataPathStr_)
        return str(self.dc.gv(_dataPath))

    def addToDataPathEventListenerList(self, dataPathStr_: str):
        if self.isDataPath(dataPathStr_):
            _dataPath: str = self.changeDataPath(dataPathStr_)
            # 没有建听过，就监听它
            if not (_dataPath in self.dataPathListenerList):
                self.dataPathListenerList.append(_dataPath)

    def removeDataPathListeners(self):
        if self.dataPathListenerList:
            _length: int = len(self.dataPathListenerList)
            for _idx in range(_length):
                self.dataEventMgr.removeEvent(self.dataPathListenerList[_idx], self)
            self.dataPathListenerList = None
