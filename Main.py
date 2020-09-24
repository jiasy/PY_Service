#!/usr/bin/env python3
import threading
import importlib
import utils
import os


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
        _app.main = self
        return _app

    def removeAppByName(self, appName_):
        _app = self.appDict[appName_]
        _app.main = None
        del self.appDict[appName_]

    def getAppWithService(self, appName_: str, serviceName_: str):
        _app = self.createAppByName(appName_)
        _app.start()
        _app.sm.switchRunningServices([serviceName_])
        return _app.sm.getServiceByName(serviceName_)


# Excel 测试专用
def excelProcessStepTest(
        baseServiceName_: str,  # 服务
        subBaseInServiceName_: str,  # 子服务
        functionName_: str,  # 功能名
        dParameters_: dict = {},
        cmdDict_: dict = None
):
    # 创建 Excel 工作流
    _main = Main()
    _excelApp = _main.createAppByName("Excel")
    _excelApp.start()
    # 切换到子服务，只为了能取得它的res路径
    _subBaseInService = _excelApp.switchTo(baseServiceName_, subBaseInServiceName_)
    # 全局常量，将路径指定到。测试用的非Excel执行命令，所以，配有配置 dGlobalDict 地方，在这里手动写入。
    _dGlobalDict = {"resFolderPath": _subBaseInService.subResPath}  # 测试使用的文件夹为子服务所对应的资源文件夹

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
                        "sBaseService": baseServiceName_,  # 服务
                        "sBaseInService": subBaseInServiceName_,  # 子服务
                        "sFunctionName": functionName_,  # 功能名
                        "sComment": "【单体测试，非Excel配置】"
                    },
                    "dParameters": dParameters_
                }
            ]
        }
    # 使用sheet和cmd构成的字典来运行
    _excelApp.runServiceByJsonDict(_sheetAndCmdDict)


def execExcelCommand(
        baseServiceName_: str,
        subBaseInServiceName_: str,
        functionName_: str,
        cmdDict_: dict = None
):
    # 创建 Excel 工作流
    _main = Main()
    _excelApp = _main.createAppByName("Excel")
    _excelApp.start()
    # 切换到子服务，只为了能取得它的res路径
    _subBaseInService = _excelApp.switchTo(baseServiceName_, subBaseInServiceName_)
    print("<模拟命令行执行>-----------------------------------------------------------------------------------------------")
    # 事例Excel路径
    _sampleExcelFilePath = os.path.realpath(
        os.path.join(
            utils.sysUtils.folderPathFixEnd(_subBaseInService.subResPath),
            subBaseInServiceName_ + ".xlsx"
        )
    )
    # 存在这个路径
    if os.path.exists(_sampleExcelFilePath):
        # excel驱动脚本
        _excelCommandPath = os.path.realpath(os.path.join(
            _sampleExcelFilePath,  # 资源中的 xlsx 路径
            os.pardir,  # BaseInService Folder
            os.pardir,  # BaseService Folder
            os.pardir,  # services Folder
            os.pardir,  # res Folder
            os.pardir,  # Excel Folder
            os.pardir,  # PY_Service Folder
            "ExcelCommand.py"  # 执行脚本名
        ))

        # 拼接驱动样例的命令
        _sampleExcelCommand = "cd '" + os.path.dirname(_sampleExcelFilePath) + "';" + \
                              "python '" + _excelCommandPath + "'" + \
                              " --excelPath '" + _sampleExcelFilePath + "'" + \
                              " --sheetName '" + functionName_ + "'"

        # 拼接命令行，
        for _key in cmdDict_:
            _sampleExcelCommand += " --" + _key + " '" + cmdDict_[_key] + "'"

        # 执行命令
        utils.cmdUtils.doStrAsCmd(
            _sampleExcelCommand,  # 执行命令行驱动 Excel 工作流配置
            os.path.dirname(_sampleExcelFilePath),  # 在子服务对应的资源目录内
            True
        )
    else:
        # 不存在
        print(
            "资源路径，对应的Excel不存在 : \n    " + _sampleExcelFilePath + "\n    " + baseServiceName_ + "->" + subBaseInServiceName_ + "->" + functionName_)
