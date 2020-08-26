#!/usr/bin/env python3
# Created by jiasy at 2020/5/24
from base.supports.Base.BaseInService import BaseInService
from utils import *


class AddStackFuncLog(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(AddStackFuncLog, self).create()

    def destory(self):
        super(AddStackFuncLog, self).destory()

    # 写入 方法 进入 的 LOG
    def getLogIn(self, fileShortName_: str, className_: str, funcName_: str, parameters_: str):
        if parameters_ == "":
            # return "#if !UNITY_EDITOR\n        LogUtils.FuncIn(System.Reflection.MethodBase.GetCurrentMethod().ReflectedType.FullName);\n#endif"
            return "        LogUtils.FuncIn(System.Reflection.MethodBase.GetCurrentMethod().ReflectedType.FullName);"
        else:
            # return "#if !UNITY_EDITOR\n        LogUtils.FuncIn(System.Reflection.MethodBase.GetCurrentMethod().ReflectedType.FullName," + parameters_ + ");\n#endif"
            return "        LogUtils.FuncIn(System.Reflection.MethodBase.GetCurrentMethod().ReflectedType.FullName," + parameters_ + ");"

    # def getLogOut(self, fileShortName_: str, className_: str, funcName_: str):
    #     _parameters = "// <---< {className},{funcName},{fileShortName}".format(
    #         fileShortName=fileShortName_,
    #         className=className_,
    #         funcName=funcName_
    #     )
    #     return _parameters

    # 对文件的方法开始结束写入LOG
    def addFuncInOutLogFolder(self, srcFolderPath_: str, targetFolderPath_: str, fileClassFuncDict_: dict):
        for _fileShortName in fileClassFuncDict_.keys():
            _fileClassDict = fileClassFuncDict_[_fileShortName]
            _filePath = srcFolderPath_ + _fileShortName
            _funcInLineDict = {}
            _funcOutLineDict = {}
            for _className in _fileClassDict.keys():
                _classFuncDict = _fileClassDict[_className]["funcDict"]
                for _funcName in _classFuncDict.keys():
                    _funcList = _classFuncDict[_funcName]
                    for _funcDict in _funcList:
                        _funcInLineDict[_funcDict["startLineIdx"]] = self.getLogIn(
                            _fileShortName,
                            _className,
                            _funcName,
                            _funcDict["parameters"]
                        )
                        # _funcReturnIdxList = _funcDict["returnLineIdxList"]
                        # for _funcReturnIdx in _funcReturnIdxList:
                        #     _funcOutLineDict[_funcReturnIdx] = self.getLogOut(_fileShortName, _className, _funcName)
                        # _funcOutLineDict[_funcDict["endLineIdx"]] = self.getLogOut(_fileShortName, _className, _funcName)
            # 读取出文件行
            _lines = fileUtils.linesFromFile(_filePath)
            _newLines = []
            for _lineIdx in range(len(_lines)):
                _line = _lines[_lineIdx]
                # if _lineIdx in _funcOutLineDict:
                #     # 结束在上一行插入
                #     _newLines.append(_funcOutLineDict[_lineIdx])
                _newLines.append(_line)
                if _lineIdx in _funcInLineDict:
                    # 开始，在下一行插入
                    _newLines.append(_funcInLineDict[_lineIdx])
            _newContent = "\n".join(_newLines)
            _targetFilePath = targetFolderPath_ + _filePath.split(srcFolderPath_).pop()
            fileUtils.writeFileWithStr(_targetFilePath, _newContent)  # 写入新文件
