#!/usr/bin/env python3
from base.supports.Base.Base import Base
from base.supports.Service.BaseService import BaseService
from utils import pyUtils
import os


class ServiceProvider(Base):

    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(ServiceProvider, self).create()

    def destory(self):
        super(ServiceProvider, self).destory()

    def getBaseObject(self, className_):
        _basePath = "base.app.services.base"
        _baseClassPath = _basePath + ("." + className_) * 3
        _baseObject = pyUtils.getObjectByClassPath(_baseClassPath, self.sm)
        # _baseObject.fullClassPath = _baseClassPath  # 变更完整路径名
        return _baseObject

    def getUtilsObject(self, className_):
        _utilsPath = "base.supports.utils"
        _utilsClassPath = _utilsPath + ("." + className_) * 2
        _utilsObject = pyUtils.getObjectByClassPath(_utilsClassPath, self.sm)
        # _utilsObject.fullClassPath = _utilsClassPath  # 变更完整路径名
        return _utilsObject

    def getServiceObject(self, appName_, className_):
        _servicePath = appName_ + ".app.services"
        _serviceClassPath = _servicePath + ("." + className_) * 3
        _serviceObject = pyUtils.getObjectByClassPath(_serviceClassPath, self.sm)
        # _serviceObject.fullClassPath = _serviceClassPath  # 变更完整路径名
        return _serviceObject

    def getAppStateObject(self, appName_):
        _appStatePath = appName_ + ("." + appName_ + "AppState") * 2
        _appStateObject = pyUtils.getObjectByClassPath(_appStatePath, self.sm)
        # _appStateObject.fullClassPath = _appStatePath  # 变更完整路径名
        return _appStateObject

    def getServiceSubObject(self, serviceObject_: BaseService, subClassName_: str):
        # 通过 APP名.app.services.服务名.文件夹名.类文件名.类名 这个类路径，创建一个实例对象
        # 所属 app 名称，转换为路径
        _servicePath = serviceObject_.app.appName + ".app.services"
        # 服务名称，转换成 路径 前缀
        _serviceClassPath = _servicePath + "." + serviceObject_.className
        # 服务所在路径下，取得对象的 文件夹名.类文件名.类名
        _serviceSubClassPath = _serviceClassPath + ("." + subClassName_) * 3
        # 创建对象
        try:
            _serviceSubObject = pyUtils.getObjectByClassPath(_serviceSubClassPath, serviceObject_)
            return _serviceSubObject
        except Exception as _err:
            print(serviceObject_.className + " 没有子服务 " + subClassName_ + "\n" + str(_err.args))
