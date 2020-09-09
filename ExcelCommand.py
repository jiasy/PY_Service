from utils import cmdUtils
from utils import sysUtils
from optparse import OptionParser
from Main import Main
import os
import sys

opsDict = {}
opsDict["sProjectFolder"] = '工程文件夹'
opsDict["sPublicType"] = '发布模式'
opsDict["excelPath"] = 'excel路径'
# 可选项
opsDict["__option__"] = ["sPublicType", "sProjectFolder"]

if __name__ == "__main__":
    _thisFilePath = os.path.dirname(os.path.realpath(__file__))
    print("脚本路径 : " + _thisFilePath)
    _pwd = sysUtils.folderPathFixEnd(os.getcwd())
    print("执行路径 : " + _pwd)

    _ops = cmdUtils.getOps(opsDict, OptionParser())
    print("脚本参数 : ")
    for _key in _ops:
        print("    " + _key + " : " + _ops[_key])

    # 创建 Excel 工作流
    _main = Main()
    _excelApp = _main.createAppByName("Excel")
    _excelApp.start()

    # excel 路径
    _excelPath = _ops["excelPath"]
    if os.path.exists(_excelPath):
        # 通过 解析 Excel 获得 执行命令信息
        _excelApp.runExcel(
            _ops["excelPath"],  # excel路径
            _pwd,  # 执行命令路径
            _ops  # 命令行参数
        )
    else:
        print("excelPath 文件不存在: \n" + _excelPath)
        sys.exit(1)
