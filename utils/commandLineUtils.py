# !/usr/bin/env python3
import subprocess


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
