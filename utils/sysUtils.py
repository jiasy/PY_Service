# !/usr/bin/env python3
import os
import sys
import platform
import subprocess


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
def getRelativePath(folderPath_:str, subFolderPath_:str):
    return str(subFolderPath_).split(folderPath_)[1]




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
