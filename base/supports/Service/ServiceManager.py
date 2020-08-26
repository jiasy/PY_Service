#!/usr/bin/env python3
from base.supports.Base.Base import Base
from base.supports.Service.ServiceProvider import ServiceProvider
from base.supports.Service.BaseService import BaseService
from typing import List
import os


class ServiceManager(Base):
    def __init__(self, app_):
        self.app = app_
        super().__init__(self)
        self.serviceProvider = ServiceProvider(self)
        # 组合次数
        self.currentCombinServiceTimes: int = 0
        # 当前运行的服务列表
        self.currentRunningServiceList: List[BaseService] = []
        self.test: BaseService = None
        self.dc = self.serviceProvider.getBaseObject("DataCenter")
        self.ec = self.serviceProvider.getBaseObject("EventCenter")

    def create(self):
        super(ServiceManager, self).create()
        self.serviceProvider.create()
        self.dc.create()
        self.ec.create()

    def destory(self):
        super(ServiceManager, self).destory()
        self.serviceProvider.destory()
        self.dc.destory()
        self.ec.destory()

    # def getFullClassPath(self, BaseSubClass_):
    #     _fullClassPathSaveInClass = BaseSubClass_.fullFilePathWithOutPy
    #     _fullClassPath = BaseSubClass_.fullClassPath
    #     if _fullClassPath:
    #         return _fullClassPath
    #     else:
    #         BaseSubClass_.fullFilePath = ".".join(_fullClassPathSaveInClass.split(self.app.mainPath)[1].split("/"))
    #         return BaseSubClass_.fullFilePath

    def getServiceByName(self, serviceName_: str):
        for _service in self.currentRunningServiceList:
            if _service.className == serviceName_:
                return _service
        return None

    def createServiceByName(self, serviceName_: str):
        return self.serviceProvider.getServiceObject(self.app.appName, serviceName_)

    # 通过当前目标的服务列表，清理掉 目标服务组合中，不存在的服务
    def switchRunningServices(self, serviceNameList_=list):
        # 重新组合的次数加一
        self.currentCombinServiceTimes = self.currentCombinServiceTimes + 1
        # 当前正在运行的服务名称集合
        _runningServiceSet = set([_service.className for _service in self.currentRunningServiceList])
        # 当前要切换的服务名称集合
        _targetServiceSet = set(serviceNameList_)
        # 不在要切换的目标内的当前服务
        _removeServiceSet: set = _runningServiceSet - _targetServiceSet
        # 获取要移除的service 实例
        _removeServiceList: List[BaseService] = [self.removeServiceByName(_serviceName) for _serviceName in
                                                 _removeServiceSet]
        # 开始移除
        for _service in _removeServiceList:
            _service.destory()

        # 在切换目标内但不在正在运行的服务集合
        _createServiceSet: set = _targetServiceSet - _runningServiceSet
        # 创建并添加服务
        _createServiceList: List[BaseService] = [self.addServiceByName(_serviceName) for _serviceName in
                                                 _createServiceSet]
        # 开始创建
        for _service in _createServiceList:
            _service.create()
        # 返回列表
        return _createServiceList

    def removeServiceByName(self, serviceName_: str):
        _service: BaseService = self.getServiceByName(serviceName_)
        self.currentRunningServiceList.remove(_service)
        return _service

    def addServiceByName(self, serviceName_: str):
        _service: BaseService = self.createServiceByName(serviceName_)
        self.currentRunningServiceList.append(_service)
        return _service
