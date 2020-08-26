#!/usr/bin/env python3
from base.supports.Base.Base import Base
from base.supports.Base.BaseInService import BaseInService
from utils import *
from typing import List


class BaseService(Base):
    def __init__(self, sm_):
        super().__init__(sm_)
        # 在当前服务下创建的对象
        self.subObjects: List[BaseInService] = []
        self.objectName: str = strUtils.lowerFirstChar(self.className)
        # 将自己的引用设置给sm
        self.sm.__setattr__(self.objectName, self)
        self.resPath: str = resUtils.getRestPathForFullClassPath(self.app.resPath, self.fullClassPath)
        # print("self.resPath = " + str(self.resPath))

    def create(self):
        super(BaseService, self).create()

    def destory(self):
        # 当前服务下创建的对象，都要随着清理掉
        while len(self.subObjects) > 0:
            _shiftItem: Base = listUtils.list_shift(self.subObjects)
            # 创建了，但是没销毁的，就销毁一次
            if _shiftItem._isCreated and not _shiftItem._isDestory:
                _shiftItem.destory()
        super(BaseService, self).destory()
        # 去除自己的引用
        self.sm.__delattr__(self.objectName)

    def getSubClassObject(self, subClassName_: str):
        _subObject: BaseInService = self.sm.serviceProvider.getServiceSubObject(self, subClassName_)
        # 服务中创建的子对象，都必须继承自Base，便于统计管理
        if not isinstance(_subObject, BaseInService):
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "subClassObject is not extends from BaseInService")
        # 服务中创建的子对象，不能是服务，免得复制粘贴代码导致的基类使用错误
        if isinstance(_subObject, BaseService):
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "subClassObject is BaseService")
        _subObject.create()
        return _subObject

    def addSubClassObject(self, subObject_):
        if not (subObject_ in self.subObjects):
            self.subObjects.append(subObject_)

    def removeSubClassObject(self, subObject_):
        if subObject_ in self.subObjects:
            self.subObjects.remove(subObject_)
