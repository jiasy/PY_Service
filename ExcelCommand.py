from utils import cmdUtils
from utils import sysUtils
from optparse import OptionParser
from Main import Main
import os
import sys

opsDict = {}
# 执行参数必须预先定义，所以，可以通过命令行替换的参数是固定的。
opsDict["projectFolderPath"] = '工程文件夹'
opsDict["executeType"] = '执行模式'
opsDict["excelPath"] = 'excel路径'
# 可选项
opsDict["__option__"] = [
    "projectFolderPath"  # 工程目录可以不写。
]


# 获取执行命令的样例
def getPythonCmdStr():
    _cmdPyFile = os.path.realpath(__file__)
    print("python " + _cmdPyFile + " --excelPath [替换成Excel文件路径] --executeType 命令行驱动")
    sys.exit(1)  # 获取样例直接退出


if __name__ == "__main__":
    # getPythonCmdStr()  # 放开注释，获取执行命令的样例。

    _thisFilePath = os.path.dirname(os.path.realpath(__file__))
    print("脚本路径 : " + _thisFilePath)
    _pwd = sysUtils.folderPathFixEnd(os.getcwd())
    print("执行路径 : " + _pwd)

    _ops = cmdUtils.getOps(opsDict, OptionParser())
    print("脚本参数 : ")
    for _key in _ops:
        print("    " + _key + " : " + _ops[_key])

    _main = Main()  # 创建 Excel 工作流
    _excelApp = _main.createAppByName("Excel")
    _excelApp.start()

    _excelPath = _ops["excelPath"]  # excel 路径
    if os.path.exists(_excelPath):  # 通过 解析 Excel 获得 执行命令信息
        try:
            _excelApp.runExcel(
                _ops["excelPath"],  # excel路径
                _pwd,  # 执行命令路径
                _ops  # 命令行参数
            )
        except Exception as e:
            print("【ERROR】 执行文件错误 : " + _excelPath
                  + "\n" + " " * 8 + "0.步骤解析未完全结束，查看Excel配置"
                  + "\n" + " " * 8 + "1.权限问题无法打开Excel"
                  + "\n" + " " * 12 + "1.1.可能是Excel未关闭"
                  + "\n" + " " * 12 + "1.2.可能是权限问题"
                  + "\n" + " " * 12 + "1.3.mac下可尝试，重启Finder解决"
                  )
            sys.exit(1)
    else:
        print("【ERROR】 excelPath 文件不存在: \n    " + _excelPath)
        sys.exit(1)
