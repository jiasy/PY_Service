#!/usr/bin/env python3
# Created by jiasy at 2020/9/28

from Excel.ExcelBaseInService import ExcelBaseInService
import os
import sys
import json
from utils import sysUtils
from utils import pyUtils
from utils import folderUtils
from utils import fileUtils

import hashlib


class EncodeHash(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "EncodeStr": {
                "type": "编码类型 md5/sha1/sha256/sha512",
                "str": "A参数",
            },
            "EncodeFolder": {
                "type": "编码类型 md5/sha1/sha256/sha512",
                "folderPath": "A参数",
                "filters": "过滤后缀",
                "createHashDictFilePath": "生成的路径和Hash值键值对json对象文件路径",
            },
        }

    def create(self):
        super(EncodeHash, self).create()

    def destory(self):
        super(EncodeHash, self).destory()

    def fileEncode(self, filePath_: str, type_: str):
        with open(filePath_, 'rb') as f:
            if type_ == "md5":
                _encodeObj = hashlib.md5()
            elif type_.strip().lower() == 'sha1':
                _encodeObj = hashlib.sha1()
            elif type_.strip().lower() == 'sha256':
                _encodeObj = hashlib.sha256()
            elif type_.strip().lower() == 'sha512':
                _encodeObj = hashlib.sha512()
            else:
                self.raiseError(pyUtils.getCurrentRunningFunctionName(), "意外的类型 : " + type_)
            _encodeObj.update(f.read())
            _hash = _encodeObj.hexdigest()
        return str(_hash).upper()

    def EncodeStr(self, dParameters_):
        _str = dParameters_["str"]
        _type = dParameters_["type"].strip().lower()
        if _type == "md5":
            _encodeStr = hashlib.md5(_str.encode()).hexdigest()
        elif _type.strip().lower() == 'sha1':
            _encodeStr = hashlib.sha1(_str.encode()).hexdigest()
        elif _type.strip().lower() == 'sha256':
            _encodeStr = hashlib.sha256(_str.encode()).hexdigest()
        elif _type.strip().lower() == 'sha512':
            _encodeStr = hashlib.sha512(_str.encode()).hexdigest()
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "意外的类型 : " + _type)
            sys.exit(1)
        return _encodeStr

    def EncodeFolder(self, dParameters_):
        _folderPath = sysUtils.folderPathFixEnd(dParameters_["folderPath"])
        _type = dParameters_["type"].strip().lower()
        _filePathList = folderUtils.getFileListInFolder(_folderPath, dParameters_["filters"])
        _createHashDictFilePath = dParameters_["createHashDictFilePath"]
        _hashDict = {}
        for _i in range(len(_filePathList)):
            _filePath = _filePathList[_i]
            _hashDict[_filePath.split(_folderPath)[1]] = self.fileEncode(_filePath, _type)
        fileUtils.writeFileWithStr(
            _createHashDictFilePath,
            str(json.dumps(_hashDict, indent=4, sort_keys=False, ensure_ascii=False))
        )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    # _functionName = "EncodeStr"
    # _parameterDict = {  # 所需参数
    #     "type": "MD5",
    #     "str": "abcdefg",
    # }

    _functionName = "EncodeFolder"
    _parameterDict = {  # 所需参数
        "type": "MD5",
        "folderPath": "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/",
        "filters": [".js"],
        "createHashDictFilePath": "/Users/jiasy/Downloads/assetsMD5JsonDict.json",
    }

    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        _parameterDict,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
