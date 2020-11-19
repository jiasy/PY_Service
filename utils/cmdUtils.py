# !/usr/bin/env python3
import os
from utils import fileUtils
from utils import listUtils
from utils import pyUtils
from utils import convertUtils
from utils import sysUtils
import subprocess
import sys
import re
import shutil


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


# 在 whichFolder_ 路径下，执行 cmdStr_ ，printPipeLines_ 为 True 并将内容输出
def doStrAsCmd(cmdStr_: str, whichFolder_: str, printPipeLines_: bool = False):
    _tabeSpace = " " * 4
    print(_tabeSpace + "Running cmd : " + cmdStr_)  # 提示正在执行
    # shell：如果该参数为 True，将通过操作系统的 shell 执行指定的命令。
    # cwd：用于设置子进程的当前目录。
    _cmdResult = subprocess.Popen(
        cmdStr_, shell=True,
        cwd=whichFolder_,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    # 子进程的PID : _cmdResult.pid
    # 发送信号到子进程 : send_signal
    # communicate 该方法会阻塞父进程，直到子进程完成
    _out, _err = _cmdResult.communicate()
    # 结果转换成行数组
    _pipeLines = _out.splitlines()
    if _cmdResult.returncode != 0:
        print(_tabeSpace + 'ERROR CODE : ' + str(_cmdResult.returncode))
        print(_tabeSpace + 'ERROR INFO : ' + str(_err))
        for _i in range(len(_pipeLines)):
            print(_tabeSpace * 2 + _pipeLines[_i])
        sys.exit(1)
    else:
        if printPipeLines_:  # 需要输出的话
            for _i in range(len(_pipeLines)):
                _currentPipLine = _pipeLines[_i]
                _currentPipLine = _tabeSpace * 2 + _currentPipLine
                print(_currentPipLine)
        print(_tabeSpace + "- EXECUTE END -")  # 执行结束
        return _pipeLines


# 执行 cmd 语句，并获得输出
def doStrAsCmdAndGetPipeline(cmdStr_: str, whichFolder_: str):
    _cmdResult = subprocess.Popen(cmdStr_, shell=True, cwd=whichFolder_, stdout=subprocess.PIPE, encoding='utf-8')
    _out, _err = _cmdResult.communicate()
    return _out.splitlines()


# 获取文件夹内的文件，权限信息，苹果环境下，携带@限制权限符
def showXattr(folderPath_: str):
    if sysUtils.os_is_mac():
        listUtils.printList(doStrAsCmdAndGetPipeline("ls -laeO@", folderPath_))

# 查权限
# ls -laeO@
# 去掉mac的xattr权限，rwx -> 111 -> 7
# chmod -R 777 'file'
def removeMacXattr(filePath_: str):
    if sysUtils.os_is_mac():
        _pipelines = doStrAsCmdAndGetPipeline("ls -laeO@", os.path.dirname(filePath_))
        _idx = 0
        while (_idx < len(_pipelines)):
            _pipeline = _pipelines[_idx]
            _fileNameWithSuffix = os.path.split(filePath_)[1]
            _fileLocateFolderPath = os.path.split(filePath_)[0]
            if _pipeline.endswith(" " + _fileNameWithSuffix):  # 找到文件所在行
                doStrAsCmd(
                    "chmod -R 666 '" + _fileNameWithSuffix + "'",
                    _fileLocateFolderPath,
                    True
                )
                for _j in range(_idx + 1, len(_pipelines)):  # 后续有可能是权限描述
                    _pipelineFollow = _pipelines[_j]
                    _beginTimeResult = re.search(r'^\s+([a-z\.\#A-Z0-9]+)\s+([-0-9]+)', _pipelineFollow)
                    if _beginTimeResult:
                        _id = convertUtils.strToInt(_beginTimeResult.group(2))
                        if _id > 0:
                            _xattr = _beginTimeResult.group(1)
                            _cmdStr = "xattr -dr '" + _xattr + "' '" + _fileNameWithSuffix + "'"
                            doStrAsCmd(_cmdStr, _fileLocateFolderPath, True)
                        else:
                            try:
                                fileUtils.replaceFileBySelf(filePath_)
                            except Exception as _err:
                                raise pyUtils.AppError(
                                    "权限-1:\n    1.关闭Excel,后重启Finder，再次进行尝试。\n    2.拷贝出来，手动删除原有，再粘贴回去。\n" +
                                    str(_err.args)
                                )
                    else:
                        _idx = _j - 1  # 当前不是属性，下一个循环，要从不是属性的位置开始。后面加，这里要减
                        break
            _idx += 1


# 获取校验参数[参数配置是已知的，无法配置未知的参数]
def getOps(opsDict_, parse_):
    # 按照参数指定设置参数解析
    for _key in opsDict_:
        _val = opsDict_[_key]
        parse_.add_option('', "--" + _key, dest=_key, help=_val)

    # 取得传入的参数
    _argsParseArr = parse_.parse_args()
    _opsDict = _argsParseArr[0]  # 这里参数值对应的参数名存储在这个_ops字典里

    _opsKeyValueDict = {}
    # 解析每一个参数
    for _key in opsDict_:
        # 可选项的话，就忽略，进行下一个
        if _key == "__option__":
            continue
        # 输出参数中没有这个key
        if not _opsDict.__dict__[_key]:
            # 如果编辑了可选项，那么可选项内的参数缺失，只提示，不报错
            if "__option__" in opsDict_ and _key in opsDict_["__option__"]:
                print("WARNING : <" + _key + ":" + opsDict_[_key] + "> 空参数")
            else:
                # 如果不在可选项中，那么就报错，停止进程
                print("ERROR : 必须有 " + _key + " -> " + opsDict_[_key])
                sys.exit(1)
        else:
            _opsKeyValueDict[_key] = _opsDict.__dict__[_key]

    # 返回为指定key的参数列表
    _opsList = _argsParseArr[1]
    return _opsKeyValueDict, _opsList


if __name__ == "__main__":
    # doStrAsCmd("PWD", "/Users/jiasy/Documents/develop/", True)
    # removeMacXattr("/Volumes/Files/develop/GitHub/PY_Service/Excel/res/services/File/MoveFiles/MoveFiles.xlsx")
    removeMacXattr("/Volumes/Files/develop/GitHub/PY_Service/Excel/res/services/Excel/ExcelToJsonFile/source/Data.xlsx")
