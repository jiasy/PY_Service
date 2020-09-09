#!/usr/bin/env python3
# Created by jiasy at 2020/9/8
from base.supports.Base.BaseInService import BaseInService
from utils import sysUtils
from utils import cmdUtils
import os


class ExecCMD(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(ExecCMD, self).create()

    def destory(self):
        super(ExecCMD, self).destory()

    def doExcelFunc(self, dParameters_: dict):
        _cmdStr = str(dParameters_["sCMD"])
        _execFolderPath = sysUtils.folderPathFixEnd(dParameters_["sExecFolderPath"])  # 路径需要确保后面有/
        cmdUtils.doStrAsCmd(_cmdStr, _execFolderPath, True)


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSp = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSp[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSp[1]  # 切到的后面就是子服务名称
    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        {  # 所需参数
            "sCMD": "PWD",
            "sExecFolderPath": "{sResPath}",  # 在子服务对应的资源目录中执行代码
        },
        {  # 命令行参数

        }
    )
