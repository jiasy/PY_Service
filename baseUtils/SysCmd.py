# !/usr/bin/env python3
import sys
from subprocess import PIPE, Popen


# ------------------------------------执行脚本---------------------------------------------------------------------------------------
def doShell(_shellScriptStr):
    # print "shell script : "+_shellScriptStr
    # shell是否为shell脚本
    _p = Popen(_shellScriptStr, shell=True, stdout=PIPE, stderr=PIPE)
    # 阻塞等待
    (stdoutdata, stderrdata) = _p.communicate()
    if _p.returncode != 0:
        print("doShell Error.")
        return -1
    else:
        # print "doShell Success."
        return 1
