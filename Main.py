#!/usr/bin/env python3
import threading
import importlib


# 根据包路径创建类的实例对象
def getObjectByClassPath(classPath_, *args):
    _modelPath, _className = classPath_.rsplit(".", 1)
    _model = importlib.import_module(_modelPath)
    # 文件内的类名和文件名保持一致
    return getattr(_model, _className)(*args)  # 反射并实例化 *args 元组拆包


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


# Main 是单子类
class Main(metaclass=SingletonType):
    def __init__(self):
        self.appDict = {}

    def createAppByName(self, appName_):
        # 文件路径 : [Moudle]/[Moudle]App.py 内有 [Moudle]App 类
        # 引用方式 : [Moudle].[Moudle]App.[Moudle]App
        _appClassPath = appName_ + "." + appName_ + "App" + "." + appName_ + "App"
        # 通过这个路径，实例化一个 App 实例。
        _app = getObjectByClassPath(_appClassPath)
        # Main 的 appDict 字典中， 会保留创建的 app 实例引用
        self.appDict[appName_] = _app
        return _app
