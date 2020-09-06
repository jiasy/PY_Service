# !/usr/bin/env python3
import os
from utils import fileUtils
import subprocess


# 将 逗号分割的字符串 加工成 参数输出,最后一个参数判断它是不是需要“'”包裹
# 将 --env DB_NAME=gitlabhq_production,DB_USER=gitlab
# 转换成--env='DB_NAME=gitlabhq_production' --env='DB_USER=gitlab'
# cmdUtils.getParameterListStr("env","DB_NAME=gitlabhq_production,DB_USER=gitlab",True)
def getParameterListStr(prefix_, listStr_, isStringBoo):
    if listStr_ == None or str(listStr_).strip() == "":
        return ""
    else:
        _strList = listStr_.split(",")
        _returnStr = ""
        for _i in range(len(_strList)):
            _returnStr += getParameterStr(prefix_, _strList[_i], isStringBoo)
        return _returnStr


# 将输入参数加工成命令行参数。
# 将 --prefix_ str_[需要引号包裹 isStringBoo = true]
# 转换成--prefix_='str_'
# cmdUtils.getParameterStr("prefix_","str_",True)
def getParameterStr(prefix_, str_, isStringBoo):
    if str_ == None or str(str_).strip() == "":
        return ""
    else:
        _returnStr = ""
        if isStringBoo:
            _returnStr = '--' + prefix_ + '=\'' + str_ + '\' '
        else:
            _returnStr = '--' + prefix_ + '=' + str_ + ' '
        return _returnStr


# 执行 cmd_ 并且记录输出 log 生成 logPath_ 文件
def doCmd(cmd_: str, logPath_: str = None):
    _exeLog = "\n".join(os.popen(cmd_).readlines())
    if logPath_:
        fileUtils.writeFileWithStr(logPath_, _exeLog)
    # 返回输出，可能调用者会有对它的判断处理
    return _exeLog


def doStrAsCmdAndGetPipe(cmdStr_: str, whichFolder_: str, printPipeLines_: bool = False):
    _tabeSpace = " " * 4
    print(_tabeSpace + "Running cmd : " + cmdStr_)  # 提示正在执行
    _cmdResult = subprocess.Popen(cmdStr_, shell=True, cwd=whichFolder_, stdout=subprocess.PIPE, encoding='utf-8')
    _out, _err = _cmdResult.communicate()
    _pipeLines = _out.splitlines()
    if _err is not None:
        print(_tabeSpace + "- ERROR -")  # 打印错误
        for _i in range(len(_pipeLines)):
            print(_tabeSpace * 2 + _pipeLines[_i])
        return False
    else:
        if printPipeLines_:  # 需要输出的话
            for _i in range(len(_pipeLines)):
                _pipeLines[_i] = _tabeSpace * 2 + _pipeLines[_i]
                print(_pipeLines[_i])
        else:
            print(_tabeSpace + "- SUCCESS -")  # 打印成功
        return True


if __name__ == "__main__":
    doStrAsCmdAndGetPipe("PWD", "/Users/jiasy/Documents/develop/", True)
