# !/usr/bin/env python3
import os
import sys
import platform
from utils import cmdUtils


# ------------------------------------系统判断---------------------------------------------------------------------------------------
def os_is_win32():
    return sys.platform == 'win32'


def os_is_32bit_windows():
    if not os_is_win32():
        return False
    arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
    archw = "PROCESSOR_ARCHITEW6432" in os.environ
    return arch == "x86" and not archw


def os_is_windows():
    return platform.system() == "Windows"


def os_is_mac():
    return platform.system() == "Darwin"


def os_is_linux():
    return platform.system() == "Linux"


# 文件夹 路径 修改
def folderPathFixEnd(path_str):
    if not os_is_win32():
        if not path_str[-1] == "/":
            return path_str + "/"
        else:
            return path_str
    if path_str.startswith("\\\\?\\"):
        return path_str
    ret = "\\\\?\\" + os.path.abspath(path_str)
    ret = ret.replace("//", "/")
    ret = ret.replace("/", "\\")
    return ret


# 获取 subFolderPath_ 相对于 folderPath_ 的路径
def getRelativePath(folderPath_: str, subFolderPath_: str):
    return str(subFolderPath_).split(folderPath_)[1]


# 文件变更执行权限
def chmod(type_: str, filePath_: str, printPipeLines_: bool = False):
    # 1 可执行 --x
    # 2 可写 -w-
    # 3 可写执行 -wx
    # 4 可读 r--
    # 5 可读执行 r-x
    # 6 可读写 rw-
    # 7 可读写执行 rwx
    if type_ == "111" or type_ == "222" or type_ == "444" or type_ == "666" or type_ == "777" or type_ == "333" or type_ == "555":
        if os_is_mac():  # mac多了一步
            cmdUtils.doStrAsCmdAndGetPipe(
                "xattr -dr com.apple.quarantine " + os.path.basename(filePath_),  # mac系统下去掉 @ 权限
                os.path.dirname(filePath_),  # 文件所在的文件夹内执行
                printPipeLines_  # 打印命令pipeline
            )
        cmdUtils.doStrAsCmdAndGetPipe(
            "chmod -R " + type_ + " " + os.path.basename(filePath_),  # 可读可写不可执行 666
            os.path.dirname(filePath_),
            printPipeLines_
        )

# ------------------------------------管道出入---------------------------------------------------------------------------------------
# cat filePath | python3.7 py脚本1 脚本参数 | python3.7 py脚本2 脚本参数
# 打开 filePath 文件，内容作为 py脚本1 的输入，py脚本1 操作之后，通过sys.stdout.write(结果)写入输出管道，作为py脚本2的输入
#     # 管道输入
#     sys.stdin
#     # 管道输出
#     sys.stdout
#     # 当前脚本
#     sys.argv[0]
#     # 脚本的第一个参数,以此类推
#     sys.argv[1]
