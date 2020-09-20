# !/usr/bin/env python3
import json
import os
from utils import sysUtils
import shutil
import chardet
import sys


def removeBomInUTF8(filePath_: str):
    '''移除UTF-8文件的BOM字节'''
    _BOM = b'\xef\xbb\xbf'
    _existBom = lambda s: True if s == _BOM else False

    _file = open(filePath_, 'rb')
    if _existBom(_file.read(3)):
        print(filePath_ + "has utf-8 bom")
        _fbody = _file.read()
        with open(filePath_, 'wb') as _file:
            _file.write(_fbody)


# 获取文件名后缀 (.jpg ...)
def getSuffix(path_: str):
    _, suffix = os.path.splitext(path_)
    return suffix


# 按照mac的路径方式填写 subPath
def getPath(rootPath_: str, subPath_: str):
    _path = subPath_.strip()
    _currentPath = rootPath_
    # 跟目录不填写，就是在当前脚本的位置向下找文件
    if _currentPath is None:
        _currentPath = os.path.dirname(os.path.realpath(__file__))

    _currentPath = os.path.normpath(_currentPath)
    _pathPieceList = _path.split(os.path.sep)  # 按照当前系统的分割符号 / 或则 \ 来分割成数组

    while len(_pathPieceList) > 0:
        _pathPiece = _pathPieceList.pop(0)
        if _pathPiece == "..":  # 上层目录
            _currentPath = os.path.join(_currentPath, os.pardir)
        elif _pathPiece == ".":
            None
        else:
            _currentPath = os.path.join(_currentPath, _pathPiece)
    _currentPath = os.path.realpath(_currentPath)
    return _currentPath


def getFileEncode(filePath_: str):
    if os.path.exists(filePath_):
        _encodeInfo = None
        try:
            _file = open(filePath_, 'rb')
            try:
                _encodeInfo = chardet.detect(_file.read())  # 得到编码信息
            finally:
                _file.close()
        except Exception as e:
            print(filePath_, e)
        if _encodeInfo:
            return _encodeInfo["encoding"]
        else:
            print(filePath_ + " : 无法获取编码信息。")
            sys.exit(1)
    else:
        print(filePath_ + " : 文件不存在。")
        sys.exit(1)


def readFromFile(filePath_: str):
    _encodeType = getFileEncode(filePath_)
    _contentStr = None
    try:
        _file = open(file=filePath_, mode='r', encoding=_encodeType)  # 按照编码打开
        try:
            _contentStr = _file.read()
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)
    return _contentStr


# 读取文件的每一行
def linesFromFile(filePath_: str):
    _encodeType = getFileEncode(filePath_)
    _lines = open(file=filePath_, mode='r', encoding=_encodeType).readlines()  # 按照编码打开
    return _lines


# 移除存在文件
def removeExistFile(path_: str):
    if os.path.exists(path_):
        os.remove(path_)
        return True
    else:
        return False


# json文件直接读取成字典
def dictFromJsonFile(jsonPath_: str):
    return json.loads(readFromFile(jsonPath_))


# 获取文件的大小,结果保留两位小数，单位为 B
def getFileSize(filePath_):
    return os.path.getsize(filePath_)


# 写文件
def writeFileWithStr(filePath_: str, str_: str):
    if not os.path.exists(os.path.dirname(filePath_)):
        os.makedirs(os.path.dirname(filePath_))
    try:
        _file = open(filePath_, 'w')
        try:
            _file.write(str_)
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)


# 对象直接写成json文件
def dictToJsonFile(filePath_: str, dict_: dict):
    _jsonStr = str(json.dumps(dict_, indent=4, sort_keys=False, ensure_ascii=False))
    return writeFileWithStr(filePath_, _jsonStr)


# folderPath_ 主要目录
# filePath_ 相对路径
def justName(filePath_: str, folderPath_: str = None):
    _filePath = filePath_
    if folderPath_:
        _filePath = sysUtils.folderPathFixEnd(folderPath_) + filePath_
    if os.path.isfile(_filePath):
        _nameSplitArr = os.path.basename(_filePath).split(".")
        if len(_nameSplitArr) > 1:
            _nameSplitArr.pop()
        _justName = ".".join(_nameSplitArr)
        return _justName
    else:
        raise Exception(
            _filePath + "不是一个文件，不可能有文件后缀，所以，不用切后缀"
        )
        return None


# folderPath_ 主要目录
# filePath_ 相对路径
def pathWithOutSuffix(filePath_: str, folderPath_: str = None):
    _filePath = filePath_
    if folderPath_:
        _filePath = sysUtils.folderPathFixEnd(folderPath_) + filePath_
    if os.path.isfile(_filePath):
        return os.path.splitext(_filePath)[0]
    else:
        raise Exception(
            _filePath + " 不是一个文件，不可能有文件后缀，所以，不用切后缀"
        )
        return None


# 文件是否含有字符串-------------------------------
# filePath_ 文件路径
# string_ 是否包含的那个字符串
def fileHasString(filePath_: str, targetStr_: str):
    _returnValue = None
    try:
        _file = open(filePath_, 'r')
        try:
            _fileLines = _file.readlines()
            _countLine = 0
            for _line in _fileLines:
                _countLine += 1
                if targetStr_ in _line:
                    _returnValue = "<" + str(_countLine) + "> " + _line
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)
    return _returnValue


# 保持文件结构，获取新文件名
def getNewNameKeepFolderStructure(
        sourceFolderPath_: str,
        targetFolderPath_: str,
        filePath_: str,
        targetSuffix_: str = None  # 需要转换后缀时，填写后缀名
):
    _sourceFolderPath = sysUtils.folderPathFixEnd(sourceFolderPath_)
    _targetFolderPath = sysUtils.folderPathFixEnd(targetFolderPath_)
    if targetSuffix_:  # 有后缀的话，就改一下
        _newFilePath = pathWithOutSuffix(filePath_).split(_sourceFolderPath)[1] + targetSuffix_
    else:  # 无后缀变换的需求，就直接用了
        _newFilePath = filePath_.split(_sourceFolderPath)[1]
    return os.path.join(
        _targetFolderPath,
        _newFilePath
    )


# 将 sourceFolderPath_ 压缩成，zipParentFolderPath_/zipName_.zip 文件
def zipFolder(sourceFolderPath_: str, zipParentFolderPath_: str, zipName_: str):
    _lastFolder = os.path.abspath('.')
    os.chdir(zipParentFolderPath_)
    shutil.make_archive(zipName_, 'zip', sourceFolderPath_)
    os.chdir(_lastFolder)


# 备份文件
def backUpFile(filePath_: str):
    _dirName = os.path.dirname(filePath_)
    _justName = justName(filePath_)
    _suffix = os.path.splitext(filePath_)[1]
    _backUpPath = os.path.join(_dirName, _justName + "_backUp." + _suffix)
    shutil.copy(filePath_, _backUpPath)
    os.remove(filePath_)
    return _backUpPath


# 自己复制出一个副本，然后，删除掉自己，再用副本替换自己
def replaceFileBySelf(filePath_: str):
    _backUpPath = backUpFile(filePath_)
    shutil.copy(_backUpPath, filePath_)
    os.remove(_backUpPath)


if __name__ == "__main__":
    getPath(None, "./a/b/pk.jpg")

'''
os中定义了一组文件、路径在不同操作系统中的表现形式参数，如下:
os.sep     --返回路径各部分之间的分隔符，linux是'/'，windows是'\\'，由于'\'在python中会转义，所以返回值是两个'\' ==　os.path.sep
os.extsep  ----- 返回文件名和文件扩展名之间的分隔符： '.'
os.pathsep ----- 目录分隔符，':'
os.linesep ----- 换行分隔符，linux是'\n'，windows是'\r\n'
'''
'''
os.path.isfile(path)     ----- 检验给出的路径是否是一个文件，返回bool值
os.path.isdir(path)      ----- 检验给出的路径是否是一个目录，返回bool值
os.path.exists(path)     ----- 检验给出的路径是否存在，返回bool值
os.path.getsize(path)    ----- 获得路径（文件或目录）的大小，如果是目录，返回0L，以字节为单位
os.path.abspath(path)    ----- 获得绝对路径
os.path.normpath(path)   ----- 规范path字符串形式，结果把/变为//
os.path.split(path)      ----- 分割路径名和文件名，返回值为tuple：(路径名，文件名.文件扩展名)，如果路径是目录，则返回：(路径名，'')
os.path.splitext(path)   ----- 分离文件名和扩展名，返回值格式：(文件名，扩展名)，如果参数是目录，则返回：(路径，'')
os.path.join(path，name) ----- 连接目录与文件名或目录，返回值为：path/name
os.path.basename(path)   ----- 返回文件名，实际上把路径的最后一个"/"分割，返回后者，目录亦如此
os.path.dirname(path)    ----- 返回文件路径，实际上是把路径的最后一个"/"分割，返回前者，目录亦如此
os.path.getatime(path)   ----- 文件或文件夹的最后访问时间，从新纪元到访问时的秒数
os.path.getmtime(path)   ----- 文件或文件夹的最后修改时间
os.path.getctime(path)   ----- 文件或文件夹的创建时间
'''
'''
from pathlib import Path
from pathlib import Path
 
data_folder = Path("source_data/text_files")


file_to_open = data_folder / "raw_data.txt"
 
print(file_to_open.name)
# prints "raw_data.txt"
 
print(file_to_open.suffix)
# prints "txt"
 
print(file_to_open.stem)
# prints "raw_data"
 
if not file_to_open.exists():
    print("Oops, file doesn't exist!")
else:
print("Yay, the file exists!")

print(file_to_open.read_text())
'''
'''
from pathlib import Path
p = Path(r'd:\test\tt.txt.bk')
p.name       # 获取文件名 # tt.txt.bk
p.stem       # 获取文件名除后缀的部分 # tt.txt
p.suffix     # 文件后缀 # .bk
p.suffixs    # 文件的后缀们... # ['.txt', '.bk']
p.parent     # 相当于dirnanme # WindowsPath('d:/test')
p.parents    # 返回一个iterable, 包含所有父目录 # <WindowsPath.parents>
p.parents    # 返回向上的目录递归路径，['d:\test','d:\']
a.parts      # 将路径通过分隔符分割成一个元祖 # ('d:\\', 'test', 'tt.txt.bk')
'''