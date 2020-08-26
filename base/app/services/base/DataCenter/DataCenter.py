#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
import json
from base.app.services.base.DataCenter.DataEventMgr.DataEventMgr import DataEventMgr
from typing import List


class DataCenter(BaseService):

    def __init__(self, sm_):
        super().__init__(sm_)
        self.dataSet: dict = dict({})
        self.ds: dict = self.dataSet
        self.dataEventMgr: DataEventMgr = DataEventMgr(self.sm)
        self.listDict: dict = dict({})

    def create(self):
        self.sm.dc = self
        super(DataCenter, self).create()
        self.dataEventMgr.create()

    def destory(self):
        self.dataEventMgr.destory()
        self.dataEventMgr = None
        super(DataCenter, self).destory()
        self.sm.dc = None

    # ---------------------------------其他 - --------------------------------

    def setValueToDataPath(self, dataPath_: str, value_, dataSet_: dict = None):
        if not self.dataPathValidation(dataPath_):
            return None
        # 发生变化的路径列表
        _changeList: List[str] = []
        # 路径切割层级列表
        _dataPathList: List[str] = []
        if dataPath_.find(".") > 0:
            _dataPathList = dataPath_.split(".")
        else:
            _dataPathList.append(dataPath_)

        # 路径初始为整体路径
        _dataPosition: dict = self.dataSet
        # 相对路径被赋值的话，就从相对路径开始查找
        if not dataSet_ is None:
            _dataPosition = dataSet_

        while len(_dataPathList) > 0:
            _currentKey = listUtils.list_shift(_dataPathList)
            # if _currentKey.find("_") > 0:
            #     self.raiseError(pyUtils.getCurrentRunningFunctionName(), "字段名不能出现下钢线 : " + _currentKey)

            if len(_dataPathList) == 0:
                if not value_:  # 之前，赋值过数组元素的数据路径，就先清理掉之前的
                    if str(_currentKey + "[1]") in _dataPosition:
                        _arrayLength = _dataPosition[_currentKey]
                        for i in range(_arrayLength):
                            _tempKey = "[" + str(i + 1) + "]"
                            del _dataPosition[_currentKey + _tempKey]
                            _changeList.append(dataPath_ + _tempKey)

                        del _dataPosition[_currentKey]
                    else:
                        del _dataPosition[_currentKey]
                elif isinstance(value_, list):
                    self.resetlistOnDataPath(_dataPosition, dataPath_, _currentKey, value_, _changeList)
                elif isinstance(value_, bool):
                    if value_:
                        _dataPosition[_currentKey] = "True"
                    else:
                        _dataPosition[_currentKey] = "False"
                    _changeList.append(dataPath_)
                elif isinstance(value_, str) or isinstance(value_, int) or isinstance(value_, float) or isinstance(
                        value_, complex):
                    _dataPosition[_currentKey] = str(value_)
                    _changeList.append(dataPath_)
                elif isinstance(value_, dict):  # 不是数字，字符串，布尔，数组，其他的就是对象了
                    if not _currentKey in _dataPosition:
                        _dataPosition[_currentKey] = dict({})
                    self.recursiveDataPath(_dataPosition[_currentKey], value_, dataPath_, _changeList)
                else:
                    self.raiseError(pyUtils.getCurrentRunningFunctionName(), "意外的类型 : " + _currentKey)
            else:
                if not _dataPosition[_currentKey]:
                    _dataPosition[_currentKey] = dict({})
                _dataPosition = _dataPosition[_currentKey]

        for i in range(len(_changeList)):
            self.dataEventMgr.onDataChange(_changeList[i])
        return _changeList

    def deleteValueByDataPath(self,
                              dataPath_: str,
                              dataSet_: dict = None
                              ):
        if not self.dataPathValidation(dataPath_):
            return False

        _dataPathList: List[str] = None
        if dataPath_.find("."):
            _dataPathList = dataPath_.split(".")
        else:
            _dataPathList.append(dataPath_)

        _dataPositionParent: dict = None
        _dataKeyInParent: str = None

        # 路径初始为整体路径
        _dataPosition: dict = self.dataSet
        # 相对路径被赋值的话，就从相对路径开始查找
        if not dataSet_ is None:
            _dataPosition = dataSet_

        while len(_dataPathList) > 0:
            _currentKey: str = listUtils.list_shift(_dataPathList)
            if not _dataPosition:
                return False

            _dataPositionParent = dict(_dataPosition)  # 记录当前为父节点
            _dataKeyInParent = _currentKey
            _dataPosition = _dataPosition[_currentKey]  # 记录当前节点

        if _dataPositionParent:
            del _dataPositionParent[_dataKeyInParent]
            return True
        return False

    # 获取路径数据
    def getValueByDataPath(self,
                           dataPath_: str,
                           dataSet_: dict = None
                           ):
        if not self.dataPathValidation(dataPath_):
            return None

        _dataPathList: List[str] = []
        if dataPath_.find("."):
            _dataPathList = dataPath_.split(".")
        else:
            _dataPathList.append(dataPath_)

        # 路径初始为整体路径
        _dataPosition: dict = self.dataSet
        # 相对路径被赋值的话，就从相对路径开始查找
        if not dataSet_ is None:
            _dataPosition = dataSet_

        while len(_dataPathList) > 0:
            _currentKey: str = listUtils.list_shift(_dataPathList)
            if _dataPosition is None:
                return None
            _dataPosition = _dataPosition[_currentKey]

        return _dataPosition

    # 遍历字段，提醒数据路径的监听者改变数据
    def recursiveDataPath(self,
                          dataOnParentPath_: dict,
                          valueDict_: dict,
                          dataPath_: str,
                          changeList_: list
                          ):
        for _key, _ in valueDict_.items():
            _currentPath: str = ""
            if dataPath_ == "":
                _currentPath = _key
            else:
                _currentPath = dataPath_ + "." + _key

            _value = valueDict_[_key]
            if isinstance(_value, list):
                self.resetlistOnDataPath(dataOnParentPath_, dataPath_, _key, _value, changeList_)
            elif isinstance(_value, bool):
                if _value:
                    dataOnParentPath_[_key] = "True"
                else:
                    dataOnParentPath_[_key] = "False"
                changeList_.append(_currentPath)
            elif (
                    isinstance(_value, str) or
                    isinstance(_value, int) or
                    isinstance(_value, float) or
                    isinstance(_value, complex)
            ):
                dataOnParentPath_[_key] = str(_value)
                changeList_.append(_currentPath)
            elif not _value:
                dataOnParentPath_[_key] = "None"
            else:
                # 没有键值，创建键值
                if not _key in dataOnParentPath_:
                    dataOnParentPath_[_key] = dict({})
                else:
                    # 有键值，但是类型不是字典
                    if not isinstance(dataOnParentPath_[_key], dict):
                        # 放弃原有键值，换成字典
                        dataOnParentPath_[_key] = dict({})

                self.recursiveDataPath(dataOnParentPath_[_key], valueDict_[_key], _currentPath, changeList_)

    # 递归设置数据
    def resetlistOnDataPath(self,
                            dataOnCurrentDataPath_: dict,
                            dataPath_: str,
                            lastKey_: str,
                            arrayValue_: list,
                            changeList_: list
                            ):
        _tempKey: str = None
        _dataPath: str = None
        _elementPath: str = None
        if lastKey_ in dataOnCurrentDataPath_:
            _arrayLength = int(dataOnCurrentDataPath_[lastKey_])
            if _arrayLength > 0:
                for i in range(_arrayLength):
                    _tempKey = "[" + str(i + 1) + "]"
                    _dataPath = lastKey_ + _tempKey
                    del dataOnCurrentDataPath_[_dataPath]
                    # _elementPath = dataPath_ + "." + _dataPath
                    # changeList_.append(_elementPath)

            changeList_.append(dataPath_)

        dataOnCurrentDataPath_[lastKey_] = len(arrayValue_)

        # if not (dataPath_ in changeList_):
        #     changeList_.append(dataPath_)

        _arrayPath = dataPath_ + "." + lastKey_

        if not (_arrayPath in changeList_):
            changeList_.append(_arrayPath)

        self.listDict[_arrayPath] = arrayValue_

        for i in range(len(arrayValue_)):
            _tempKey = "[" + str(i + 1) + "]"
            _dataPath = lastKey_ + _tempKey
            _dataElement = arrayValue_[i]
            if isinstance(_dataElement, bool):
                if _dataElement:
                    dataOnCurrentDataPath_[_dataPath] = "True"
                else:
                    dataOnCurrentDataPath_[_dataPath] = "False"
                _elementPath = dataPath_ + "." + _dataPath
                changeList_.append(_elementPath)
            elif (
                    isinstance(_dataElement, str) or
                    isinstance(_dataElement, int) or
                    isinstance(_dataElement, float) or
                    isinstance(_dataElement, complex)
            ):
                dataOnCurrentDataPath_[_dataPath] = _dataElement
                _elementPath = dataPath_ + "." + _dataPath
                changeList_.append(_elementPath)
            elif not _dataElement:
                dataOnCurrentDataPath_[_dataPath] = "None"
                _elementPath = dataPath_ + "." + _dataPath
                changeList_.append(_elementPath)
            else:
                _dataOnPath = dict({})
                dataOnCurrentDataPath_[_dataPath] = _dataOnPath
                _elementPath = dataPath_ + "." + _dataPath
                self.recursiveDataPath(_dataOnPath, _dataElement, _elementPath, changeList_)
                if not (_elementPath in changeList_):
                    changeList_.append(_elementPath)

    def printData(self, dataSet_: dict, currentPath_: str):
        for _key, _ in dataSet_.items():
            _currentPath: str = ""
            if currentPath_ == "":
                _currentPath = _key
            else:
                _currentPath = currentPath_ + "." + _key

            _value = dataSet_[_key]
            if (
                    isinstance(_value, str) or
                    isinstance(_value, int) or
                    isinstance(_value, bool) or
                    isinstance(_value, float) or
                    isinstance(_value, complex)
            ):
                print(_currentPath + " : " + str(_value))
            elif isinstance(_value, list):
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                "ERROR DataCenter -> printData : 转换完的数据不可能出现 数组")
            else:
                self.printData(_value, _currentPath)

    # 简单写，因为经常使用所以写的短一些
    def gv(self, dataPath_: str, dataSet_: dict = None):
        # 通过数据路径获取数据
        return self.getValueByDataPath(dataPath_, dataSet_)

    # 删除对应路径的数据
    def dv(self, dataPath_: str, dataSet_: dict = None):
        return self.deleteValueByDataPath(dataPath_, dataSet_)

    # 给数据路径设置数据
    def sv(self, dataPath_: str, value_, dataSet_: dict = None):
        return self.setValueToDataPath(dataPath_, value_, dataSet_)

    # 将数据key排序，然后，获取排序后的Value构成的list
    def gvDictAsList(self, dataPath_: str, dataSet_: dict = None):
        _dataObject = self.gv(dataPath_, dataSet_)
        _keySortedValueArr = self.sm.arrayUtils.getValueListFromDictObject(_dataObject)
        return _keySortedValueArr

    # 获取列表元素
    def getListElement(self, listDataPath_: str, idx_: int, dataSet_: dict = None):
        _listLength: int = self.gv(listDataPath_, dataSet_)
        if not _listLength is None:
            if idx_ < _listLength:
                _propertyNameOfIdx = listDataPath_ + "[" + str(idx_ + 1) + "]"
                return self.gv(_propertyNameOfIdx, dataSet_)
            else:
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                "数组索引越界 _idx ： " + str(idx_) + " ，_listLength : " + str(_listLength))
        else:
            return None

    def printDataSetJsonString(self):
        print("dataSet = " + json.dumps(self.dataSet, indent=4, sort_keys=False, ensure_ascii=False))

    def printDataSet(self):
        self.printData(self.dataSet, "dataSet")

    def dataPathValidation(self, dataPath_: str):
        if dataPath_.find("..") >= 0:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "数据路径不能包含..")
            return False
        elif dataPath_.find("\n") >= 0 or dataPath_.find("\r") >= 0:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "数据路径不能包含 换行")
            return False
        return True

    def isDataPathExist(self, dataPath_: str):
        if self.dataPathValidation(dataPath_) is None:
            return None
        _dataObject = self.gv(dataPath_)
        if _dataObject is None:
            return None
        return _dataObject
