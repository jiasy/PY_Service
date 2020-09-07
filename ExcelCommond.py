from utils import cmdUtils
from optparse import OptionParser

opsDict = {}
# 必选项
opsDict["projectFolder"] = '工程文件夹'
opsDict["publicType"] = '发布模式'
opsDict["excelPath"] = 'excel路径'
# 可选项
opsDict["__option__"] = ["option_1", "option_2"]

if __name__ == "__main__":
    _ops = cmdUtils.getOps(opsDict, OptionParser())
    for _key in _ops:
        print(_key + " : " + _ops[_key])

