# !/usr/bin/env python3
import os
from utils import fileUtils
from utils import listUtils
import subprocess
import sys


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


# 在 whichFolder_ 路径下，执行 cmdStr_ ，printPipeLines_ 为 True 并将内容输出
def doStrAsCmd(cmdStr_: str, whichFolder_: str, printPipeLines_: bool = False):
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
        print(_tabeSpace + "- SUCCESS -")  # 打印成功
        return True


# 执行 cmd 语句，并获得输出
def doStrAsCmdAndGetPipeline(cmdStr_: str, whichFolder_: str):
    _cmdResult = subprocess.Popen(cmdStr_, shell=True, cwd=whichFolder_, stdout=subprocess.PIPE, encoding='utf-8')
    _out, _err = _cmdResult.communicate()
    return _out.splitlines()


# 获取文件夹内的文件，权限信息，苹果环境下，携带@限制权限符
def showXattr(whichFolder_: str):
    listUtils.printList(doStrAsCmdAndGetPipeline("ls -laeO@", whichFolder_))


# 获取校验参数
def getOps(opsDict_, parse_):
    # 按照参数指定设置参数解析
    for _key in opsDict_:
        _val = opsDict_[_key]
        parse_.add_option('', "--" + _key, dest=_key, help=_val)

    # 取得传入的参数
    _ops = parse_.parse_args()[0]  # 这里参数值对应的参数名存储在这个_ops字典里

    _opsKeyValueDict = {}
    # 解析每一个参数
    for _key in opsDict_:
        # 可选项的话，就忽略，进行下一个
        if _key == "__option__":
            continue
        # 输出参数中没有这个key
        if not _ops.__dict__[_key]:
            # 如果编辑了可选项，那么可选项内的参数缺失，只提示，不报错
            if "__option__" in opsDict_ and _key in opsDict_["__option__"]:
                print("WARNING : <" + _key + ":" + opsDict_[_key] + "> 空参数")
            else:
                # 如果不在可选项中，那么就报错，停止进程
                print("ERROR : 必须有 " + _key + " -> " + opsDict_[_key])
                sys.exit(1)
        else:
            _opsKeyValueDict[_key] = _ops.__dict__[_key]

    return _opsKeyValueDict


if __name__ == "__main__":
    doStrAsCmd("PWD", "/Users/jiasy/Documents/develop/", True)
