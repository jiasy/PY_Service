#!/usr/bin/env python3
import threading
import importlib
import utils


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


# Excel 测试专用
def excelProcessStepTest(
        baseServiceName_: str,
        subBaseInServiceName_: str,
        dParameters_: dict = {},
        dGlobalDict_: dict = None,
        cmdDict_: dict = None
):
    # 创建 Excel 工作流
    _main = Main()
    _excelApp = _main.createAppByName("Excel")
    _excelApp.start()
    # 切换到子服务，只为了能取得它的res路径
    _subBaseInService = _excelApp.switchTo(baseServiceName_, subBaseInServiceName_)
    # 全局常量，将路径指定到
    _dGlobalDict = {
        "sResPath": _subBaseInService.resPath
    }
    # 有指定覆盖的内容，就合并
    if dGlobalDict_:
        utils.jsonUtils.mergeAToB(dGlobalDict_, _dGlobalDict)

    # 有命令行指定参数，使用命令行的指定参数
    if cmdDict_:
        utils.jsonUtils.mergeAToB(cmdDict_, _dGlobalDict)

    # 构建Excel所能导出的格式
    _sheetAndCmdDict = \
        {
            "dGlobalDict": _dGlobalDict,
            "lProcessSteps": [
                {
                    "dServiceInfo": {
                        "sBaseService": baseServiceName_,
                        "sBaseInService": subBaseInServiceName_
                    },
                    "dParameters": dParameters_
                }
            ]
        }

    # 使用sheet和cmd构成的字典来运行
    _excelApp.runServiceByJsonDict(_sheetAndCmdDict)
