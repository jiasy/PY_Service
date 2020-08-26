#!/usr/bin/env python3
from utils import pyUtils
import Main
from typing import List


class Base(object):
    # 内存中创建成功
    def __init__(self, sm_):
        self.className: str = self.__class__.__name__
        self.sm = sm_
        self.fullClassPath: str = self.__class__.__module__
        _dotClassName = "." + self.className
        self.fullClassPath = self.fullClassPath.replace(_dotClassName * 2, _dotClassName)
        self.app = self.sm.app
        # 初始化变量
        self._isCreated: bool = False
        self._isDestory: bool = False

    # # 内存内删除成功
    # def __del__(self):
    #     # print(self.app.appName + " <- " + self.className.ljust(25, " ") + '__del__ : ' + str(self.app.baseCount))

    # 获取当前App内，这个Base继承类，创建的对象的列表
    def getRunningBaseObjectListBelongToThisClass(self):
        _runtimeObjectInfoDict: dict = self.app.runtimeObjectInfoDict
        if not self.fullClassPath:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "self.fullClassPath is None")
        _currentObjectList: List[Base] = None
        if self.fullClassPath in _runtimeObjectInfoDict:
            _currentObjectList = _runtimeObjectInfoDict[self.fullClassPath]
        else:
            _currentObjectList = []
            _runtimeObjectInfoDict[self.fullClassPath] = _currentObjectList
        return _currentObjectList

    # 服务化逻辑内的创建
    def create(self):
        if self._isDestory:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "is already destory ~ !")
        if self._isCreated:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "is already _isCreated ~ !")
        self._isCreated = True
        # 累计 Base 的对象
        self.app.baseCount = self.app.baseCount + 1
        self.getRunningBaseObjectListBelongToThisClass().append(self)
        # print("  <-- " + self.app.appName + "." + self.className.ljust(20) + "> create " + + str(self.app.baseCount))

    # 服务化逻辑内的销毁
    def destory(self):
        if not self._isCreated:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "is not create ~ !")
        self._isDestory = True
        # 清除累计
        self.app.baseCount = self.app.baseCount - 1
        self.app.runtimeObjectInfoDict[self.fullClassPath].remove(self)
        # print("  --> " + self.app.appName + "." + self.className.ljust(20) + "< destory "+ str(self.app.baseCount))

    '''
            # 获取另外一个正在运行的App
            _testApp = self.getRunningAppByName("SparkTest")
            if _testApp:
                print("_testApp.appName = " + str(_testApp.appName))
            # 获取另外一个App 中正在运行的服务
            _testApptestService = self.getRunningServiceByName("SparkTest", "SparkTest")
            if _testApptestService:
                print("_testApptestService.className = " + str(_testApptestService.className))
    '''

    def getRunningAppByName(self, appName_):
        _main = Main.Main()
        _appDict: dict = _main.appDict
        if appName_ in _appDict.keys():
            return _appDict[appName_]
        else:
            return None

    def getRunningServiceByName(self, appName_, serviceName_):
        _main = Main.Main()
        _appDict: dict = _main.appDict
        _app = None
        if appName_ in _appDict.keys():
            _app = _appDict[appName_]
        _service = None
        if _app:
            _service = _app.sm.getServiceByName(serviceName_)
        return _service

    # 封装一下报错信息
    def raiseError(self, funcName_, errorStr_):
        self.app.info.raiseERR(self.className + " -> " + funcName_ + " : " + errorStr_)

    # 显示下当前内存中所有的类
    def showCurrentBaseObejctsInfo(self):
        # currentRunningBaseClassNames = {
        #     _baseObjectArr[0].className  # 取数组第一个元素
        #     for _, _baseObjectArr in self.app.runtimeObjectInfoDict.items()  # 遍历字典项
        #     if _baseObjectArr and len(_baseObjectArr) > 0  # 有且有元素
        # } # 默认有序集合
        # print("currentRunningBaseClassNames = " + str(currentRunningBaseClassNames))
        print("baseObject in < {appName} > ram : ".format(appName=self.app.appName))
        for _className, _baseObjectArr in self.app.runtimeObjectInfoDict.items():
            if _baseObjectArr and len(_baseObjectArr) > 0:
                print("    {className} : {objectNum}".format(className=_className, objectNum=len(_baseObjectArr)))
