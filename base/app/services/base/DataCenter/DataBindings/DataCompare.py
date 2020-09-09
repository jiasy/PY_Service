#!/usr/bin/env python3
from typing import List

from base.app.services.base.DataCenter.DataBindings.DataBase import DataBase
from utils import strUtils
from utils import pyUtils


class DataCompare(DataBase):

    def __init__(self, sm_):
        super().__init__(sm_)
        self.firstValue: str = None
        self.compareType: str = None
        self.secondArr: List[str] = None

    def create(self):
        super(DataCompare, self).create()

    def destory(self):
        super(DataCompare, self).destory()
        self.firstValue = None
        self.compareType = None
        self.secondArr = None

    def resetDataPath(self, dataPath_: str):
        super(DataCompare, self).resetDataPath(dataPath_)
        _dataStr: str = self.getValue(self.dataPath)
        self.resetByStr(_dataStr)

    def recreateListeners(self, dataStr_: str):
        _compareMode: str = None
        if dataStr_.find('(') >= 0 and dataStr_.find(')') >= 0:
            _compareMode = '()'
        elif dataStr_.find('(') >= 0 and dataStr_.find(']') >= 0:
            _compareMode = '(]'
        elif dataStr_.find('[') >= 0 and dataStr_.find(')') >= 0:
            _compareMode = '[)'
        elif dataStr_.find('[') >= 0 and dataStr_.find(']') >= 0:
            _compareMode = '[]'
        elif dataStr_.find('>=') > 0:
            _compareMode = '>='
        elif dataStr_.find('<=') > 0:
            _compareMode = '<='
        elif dataStr_.find('>') > 0:
            _compareMode = '>'
        elif dataStr_.find('<') > 0:
            _compareMode = '<'
        elif dataStr_.find('==') > 0:
            _compareMode = '=='
        elif dataStr_.find('!=') > 0:
            _compareMode = '!='

        if _compareMode:
            _compareArr: List[str] = dataStr_.split(_compareMode)
            self.firstValue = _compareArr[0]
            self.compareType = _compareMode
            if _compareArr[1].find(',') > 0:
                self.secondArr = _compareArr[1].split(',')
            else:
                self.secondArr = [_compareArr[1]]
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                            dataStr_ + " , 没有比较字符串")

        # 清理原有数据
        self.removeDataPathListeners()
        # 重新监听数据
        self.dataPathListenerList = []
        # 重新，监听数据路径
        self.addToDataPathEventListenerList(self.firstValue)
        _length: int = len(self.secondArr)
        for i in range(_length):
            self.addToDataPathEventListenerList(self.secondArr[i])

    # 返回一个二元组，(是否成功，数据变化之后重新计算的结果)
    def dataChanged(self):
        _arr: list = []
        _firstValue: str = self.getRealValue(self.firstValue)
        _arr.append(_firstValue)
        _arr.append(self.compareType)
        _length: int = len(self.secondArr)
        for _idx in range(_length):
            _arr.append(self.getRealValue(self.secondArr[_idx]))
        # 获取比较结果 1-成功，0-失败，-1-无解
        _compare_result: int = self.dataCompare(_arr)
        if _compare_result == -1:
            self.printResult(-1)
            self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                            "比较数据无解")
            return False, None
        if self.displayObject:
            if _compare_result == 0:
                # 不显示
                return True, False
            else:
                # 显示
                return True, True
        else:
            if _compare_result == 0:
                return True, False
            elif _compare_result == 1:
                return True, True

    def printResult(self, result_: int):
        print(self.dataStr + " :  //////////////////// " + result_)
        print("    firstValue   : " + self.firstValue)
        print("    compareType  : " + self.compareType)
        print("    secondArr : ")
        _length: int = len(self.secondArr)
        for _idx in range(_length):
            _secondValue: str = self.secondArr[_idx]
            if _secondValue.find(".") > 0:
                print("         " + _secondValue + " : " + self.dc.getValueByDataPath(_secondValue))
            else:
                print("         " + _secondValue)

    def dataCompare(self, paramsArray_: list):
        _targetValueStr: str = paramsArray_[0]
        _mode: str = paramsArray_[1]
        _value1Str: str = paramsArray_[2]
        _value2Str: str = None
        if len(paramsArray_) > 3:
            _value2Str = paramsArray_[3]

        def isNaN(dataCompareObject_: DataCompare, valueC1_: str, valueC2_: str, valueC3_: str = None):
            if (
                    strUtils.is_number(valueC1_) and
                    strUtils.is_number(valueC2_)
            ):
                _valueArr = [float(valueC1_), float(valueC2_)]
                if valueC3_:
                    if not strUtils.is_number(valueC3_):
                        dataCompareObject_.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                                      "WARN : 进行比较的数值，非数字类型无法比较 " + _mode + " : " + valueC1_ + "," + valueC2_ + "," + valueC3_)
                        return None
                    else:
                        _valueArr.append(float(valueC3_))
                return _valueArr
            else:
                dataCompareObject_.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                              "WARN : 进行比较的数值，非数字类型无法比较 " + _mode + " : " + valueC1_ + "," + valueC2_)
                return None

        _backValue: int = -1
        _numberArr: list = isNaN(self, _targetValueStr, _value1Str, _value2Str)
        if _numberArr:
            _targetValue: float = _numberArr[0]
            _value1: float = _numberArr[1]
            _value2: float = None
            if len(_numberArr) > 2:
                _value2 = _numberArr[2]

            if _mode == "()":  # x< n <y
                if _value1 < _targetValue < _value2:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "(]":  # x< n <=y
                if _value1 < _targetValue <= _value2:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "[)":  # x<= n <y
                if _value1 <= _targetValue < _value2:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "[]":  # x<= n <=y
                if _value1 <= _targetValue <= _value2:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == ">=":
                if _targetValue >= _value1:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "<=":
                if _targetValue <= _value1:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "<":
                if _targetValue < _value1:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == ">":
                if _targetValue > _value1:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "==":
                if _targetValue == _value1:
                    _backValue = 1
                else:
                    _backValue = 0
            elif _mode == "!=":
                if not (_targetValue == _value1):
                    _backValue = 1
                else:
                    _backValue = 0
            else:
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                "不存在比较模式 : " + _mode)
                return None
            return _backValue
