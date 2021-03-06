#!/usr/bin/env python3
# Created by jiasy at 2020/9/28

from Excel.ExcelBaseInService import ExcelBaseInService
import os
from utils import sysUtils
from utils import cmdUtils
from utils import pyUtils

'''
Unity C# 相关 API
平台
    当前的平台
        EditorUserBuildSettings.activeBuildTarget
    平台参数
        BuildTarget.Android
        BuildTarget.iOS
        BuildTarget.StandaloneWindows
            IntPtr.Size == 4 // 32 位
            IntPtr.Size == 8 // 64 位
     判断平台
        EditorUserBuildSettings.activeBuildTarget == BuildTarget.Android
     切换平台
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android);
命令行获取和判断
    static string GetCommandValueByKey(string parameterKey_){
        foreach (var _keyAndValue in Environment.GetCommandLineArgs()){
            if (_keyAndValue.ToLower().StartsWith(parameterKey_ + "=")){
                return _keyAndValue.Split('=')[1];
            }
        }
        return null
    }
    var _parameterValue = GetCommandValueByKey("parameterKey");
    bool _boolValue = false;//默认值
    if (!string.IsNullOrEmpty(_parameterValue)){
        _boolValue = bool.Parse(_parameterValue);//设定值
    }
    string _strValue = "default";//默认值
    if (!string.IsNullOrEmpty(_parameterValue)){
        _strValue = _parameterValue;//设定值
        if(_strValue.ToLower().Equals("ios")){//平台或其他指定
            //平台指定操作
        }
    }
'''

class BuildUnity(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "BuildIOS": {
                "unityPath": "Unity路径",
                "projectPath": "Unity工程",
                "version": "版本号",
                "bundle": "构建号",
                "platform": "平台",
                "logFile": "日志路径"
            },

        }

    def create(self):
        super(BuildUnity, self).create()

    def destory(self):
        super(BuildUnity, self).destory()

    def BuildIOS(self, dParameters_):
        _unityPathPath = dParameters_["unityPath"]
        _projectPath = sysUtils.folderPathFixEnd(dParameters_["projectPath"])
        _version = dParameters_["version"]
        _bundle = dParameters_["bundle"]
        _platform = dParameters_["platform"]
        _logFile = dParameters_["logFile"]
        _executeMethod = None

        if _platform == "iOS":
            _executeMethod = "platformBuild.BuildIOS"
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                            " platform 不支持")
        _cmdStr = _unityPathPath + " -quit -batchmode -projectPath " + _projectPath + " -executeMethod " + _executeMethod + " " + _version + " " + _bundle + " -buildTarget " + _platform + " -logFile " + _logFile

        # 执行命令
        cmdUtils.doStrAsCmd(
            _cmdStr,
            _projectPath,
            False
        )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    _functionName = "BuildIOS"
    _parameterDict = {  # 所需参数
        "unityPath": "/Volumes/Files/Applications/2019.4.10f1/Unity.app/Contents/MacOS/Unity",
        "projectPath": "/Volumes/18604037792/develop/ShunYuan/NewFarm/",
        "version": "1.000",
        "bundle": "1000",
        "platform": "iOS",
        "logFile": "/Volumes/18604037792/develop/ShunYuan/NewFarm/log.txt"
    }

    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        _parameterDict,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )

    # Main.execExcelCommand(
    #     _baseServiceName,
    #     _subBaseInServiceName,
    #     _functionName,
    #     {  # 命令行参数
    #         "executeType": "单体测试"
    #     }
    # )
