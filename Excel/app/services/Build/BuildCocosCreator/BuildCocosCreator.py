#!/usr/bin/env python3
# Created by jiasy at 2020/9/28

from Excel.ExcelBaseInService import ExcelBaseInService
import os
from utils import sysUtils
from utils import cmdUtils


class BuildCocosCreator(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "Build": {
                "cocosCreatorAppPath": "cocosCreator的位置",
                "projectFolderPath": "工程目录",
            },
        }

    def create(self):
        super(BuildCocosCreator, self).create()

    def destory(self):
        super(BuildCocosCreator, self).destory()

    def Build(self, dParameters_):
        dParameters_["projectFolderPath"] = sysUtils.folderPathFixEnd(dParameters_["projectFolderPath"])
        _cmd = "{cocosCreatorAppPath} " \
               "--path {projectFolderPath}  " \
               "--build \"configPath={projectFolderPath}WeChatGameConfig.json\""
        _cmd = _cmd.format(**dParameters_)
        print('Execute : \n    ' + str(_cmd))
        cmdUtils.doStrAsCmd(_cmd, dParameters_["projectFolderPath"], True)


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    _functionName = "Build"
    _parameterDict = {  # 所需参数
        "cocosCreatorAppPath": "/Applications/CocosCreator/Creator/2.3.3/CocosCreator.app/Contents/MacOS/CocosCreator",
        "projectFolderPath": "/Volumes/18604037792/develop/ShunYuan/wxGame/",
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

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试",
            "projectFolderPath": "/Volumes/18604037792/develop/ShunYuan/wxGame/",
            "publicType": "test",
            "version": "1146",
        }
    )
