#!/usr/bin/env python3
# Created by jiasy at 2020/5/23
from base.supports.Base.BaseInService import BaseInService
from utils import *
import re


class AnalyseStructure(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(AnalyseStructure, self).create()

    def destory(self):
        super(AnalyseStructure, self).destory()

    # 文件内的类和方法，参数控制是否包含有命名空间指定的类和方法
    def analyseFileInfo(self, srcFolderPath_: str, fileShortNameList_: list = []):
        _csCodeFolder = fileUtils.getPath(srcFolderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        _finalfileDict = {}
        for _path in _filePathList:
            _fileShortName = _path.split(srcFolderPath_).pop()
            _isFilter = False
            for _filterFileShortName in fileShortNameList_:  # 遍历过滤列表
                if _fileShortName.find(_filterFileShortName) >= 0:  # 存在过滤，就跳过
                    print("pass : " + _path)
                    _isFilter = True
                    continue
            if _isFilter:
                continue
            print("analyse : " + _fileShortName)
            _lines = fileUtils.linesFromFile(_path)
            # 类中的Class信息
            _classDictList = self.getClassList(_lines, 0, len(_lines) - 1, True)
            _fileDict = {}
            _finalfileDict[_fileShortName] = _fileDict
            for _classDict in _classDictList:
                _fileDict[_classDict["className"]] = _classDict
                del _classDict["className"]
        return _finalfileDict

    # 命名空间内的类和方法
    def analyseNameSpaceInfo(self, srcFolderPath_: str):
        _csCodeFolder = fileUtils.getPath(srcFolderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        _finalNameSpaceDict = {}
        for _path in _filePathList:
            print(_path)
            _nameSpaceDictList = self.getClassListWithNameSpace(_path)
            for _nameSpaceDict in _nameSpaceDictList:
                if _nameSpaceDict["namespace"] in _finalNameSpaceDict:  # 当前命名空间存在
                    _targetNameSpaceDict = _finalNameSpaceDict[_nameSpaceDict["namespace"]]
                else:  # 当前命名空间不存在
                    _targetNameSpaceDict = {}
                    _finalNameSpaceDict[_nameSpaceDict["namespace"]] = _targetNameSpaceDict
                for _key in _nameSpaceDict.keys():
                    if not _key == "namespace":  # 不是 namespace 的标示名
                        _targetNameSpaceDict[_key] = _nameSpaceDict[_key]  # 将类键值传递给命名空间总汇对象
        return _finalNameSpaceDict

    # 命名空间的起始和结束
    def getClassListWithNameSpace(self, path_: str):
        _lines = fileUtils.linesFromFile(path_)
        _lineLength = len(_lines)
        _nameSpaceDictList = []
        for _lineIdx in range(_lineLength):
            _line = _lines[_lineIdx]
            _nameSpaceStr = r'^\s*namespace\s+([a-zA-Z0-9_\.]+)\s+\{'
            _nameSpaceReg = re.search(_nameSpaceStr, _line)
            if _nameSpaceReg:
                _nameSpace = _nameSpaceReg.group(1)
                _nameSpaceDict = {}
                _nameSpaceDict["namespace"] = _nameSpace
                _nameSpaceDictList.append(_nameSpaceDict)
                # 从下一行开始找，找到第一个没有闭合的 },就是当前 { 对应的
                _lineAndCharIdx = self.belongToService.curlyBraces.getCloseCurlyBraces(_lineIdx + 1, _lines)
                if not _lineAndCharIdx == None:
                    _closeLine = _lines[_lineAndCharIdx[0]]
                    if not _closeLine.strip() == "}":
                        self.raiseError(
                            pyUtils.getCurrentRunningFunctionName(), " <closed,but not }> : " + _closeLine
                        )
                    else:
                        # 正确情况下记录
                        _classDictList = self.getClassList(_lines, _lineIdx, _lineAndCharIdx[0])
                        for _classDict in _classDictList:
                            _nameSpaceDict[_classDict["className"]] = _classDict
                            del _classDict["className"]
                        _lineIdx = _lineAndCharIdx[0]
                else:
                    self.raiseError(
                        pyUtils.getCurrentRunningFunctionName(), " : not close"
                    )
            else:
                if _line.find("namespace ") >= 0:
                    print("namespace Warning : " + str(_line))
        return _nameSpaceDictList

    def getExtendsClassList(self, extendsStr_):
        _charIdx = 0
        _length = len(extendsStr_)
        _count = 0
        _realClassStr = ""
        while _charIdx < _length:
            _char = extendsStr_[_charIdx]
            if _char == "<":
                _count = _count + 1
            elif _char == ">":
                _count = _count - 1
            else:
                if _count == 0:
                    _realClassStr = _realClassStr + _char
            _charIdx = _charIdx + 1
        _extendsClassList = _realClassStr.split(",")
        _finalList = []
        for _extendsClass in _extendsClassList:
            _finalList.append(_extendsClass.strip())
        return _finalList

    def getClassList(self, lines_: list, startIdx_: int, endIdx_: int, skipNamespace_: bool = True):
        _classList = []
        for _lineIdx in range(startIdx_, endIdx_):
            _line = lines_[_lineIdx]
            # 需要过滤命名空间
            if skipNamespace_:
                # 跳过命名空间所在的行
                _nameSpaceStr = r'^\s*namespace\s+([a-zA-Z0-9_\.]+)\s+\{'
                _nameSpaceReg = re.search(_nameSpaceStr, _line)
                if _nameSpaceReg:
                    _lineAndCharIdx = self.belongToService.curlyBraces.getCloseCurlyBraces(_lineIdx + 1, lines_)
                    if _lineAndCharIdx == None:
                        self.raiseError(
                            pyUtils.getCurrentRunningFunctionName(), " : not close"
                        )
                    # 匹配成功，且能找到闭合位置，就跳到闭合位置
                    _lineIdx = _lineAndCharIdx[0]
                    continue

            # # 变量 protected float _elementWidth;
            # _variableReg = re.search(r'(\w+)\s+(\w+)\s+(\w+)\s*;', _line)
            # # 变量赋值 protected int _contentLength = 0;
            # _variableReg = re.search(r'(\w+)\s+(\w+)\s+(\w+)\s*=\s*(.*)\s*;', _line)
            # # 数组
            #
            # # List
            #
            # # 枚举
            #
            # # get - set

            _classStr = r'^([a-zA-Z\s]*)\s+class\b\s+([\<\w\>]*)\s*(:|)\s*(.*)\s*\{'
            _classReg = re.search(_classStr, _line)
            if _classReg:
                _classDict = {}
                _classDict["funcDict"] = {}
                _classDict["isAbstract"] = False
                _classDict["isStatic"] = False
                _classDict["isPartial"] = False
                _classDict["isSealed"] = False
                _classDict["type"] = "private"
                _classDict["extendsFrom"] = []
                _prefix = _classReg.group(1)  # 前面有字符标示
                _prefix = strUtils.spacesReplaceToSpace(_prefix)  # 去掉两侧空格
                if not (_prefix == "" or _prefix == " "):
                    _prefixArr = _prefix.split(" ")  # 切分
                    for _prefixElement in _prefixArr:
                        if _prefixElement == "abstract":
                            _classDict["isAbstract"] = True
                        elif _prefixElement == "partial":
                            _classDict["isPartial"] = True
                        elif _prefixElement == "static":
                            _classDict["isStatic"] = True
                        elif _prefixElement == "sealed":
                            _classDict["isSealed"] = True
                        elif _prefixElement in self.belongToService.classTypeList:
                            _classDict["type"] = _prefixElement
                        else:
                            self.raiseError(
                                pyUtils.getCurrentRunningFunctionName(),
                                _classReg.group(
                                    0) + "\n" + "class split element : \'" + _prefixElement + "\' not define."
                            )

                _className = _classReg.group(2)
                if _className.find("<") > 0:
                    _className = _className.split("<")[0]  # 只要类名，不要泛型

                _classDict["className"] = _className.strip()

                _splitStr = _classReg.group(3)
                if _splitStr == ":":
                    _suffix = _classReg.group(4)
                    if _suffix.find("where ") > 0:
                        _suffix = _suffix.split("where ")[0]
                    _suffix = strUtils.spacesReplaceToSpace(_suffix)  # 去掉两侧空格
                    _classDict["extendsFrom"] = self.getExtendsClassList(_suffix)  # 获取继承类
                _classList.append(_classDict)
                _lineAndCharIdx = self.belongToService.curlyBraces.getCloseCurlyBraces(_lineIdx + 1, lines_)
                if not _lineAndCharIdx == None:
                    _closeLine = lines_[_lineAndCharIdx[0]]
                    if not _closeLine.strip() == "}" and not _closeLine.strip() == "};":
                        self.raiseError(
                            pyUtils.getCurrentRunningFunctionName(),
                            " <closed,but not }> : " + _closeLine
                        )
                    else:
                        # 正确情况下记录
                        _funcDictList = self.getFuncList(lines_, _lineIdx, _lineAndCharIdx[0])
                        for _funcDict in _funcDictList:
                            _funcName = _funcDict["funcName"]
                            if not _funcName in _classDict["funcDict"].keys():
                                _classDict["funcDict"][_funcName] = []
                            _classDict["funcDict"][_funcName].append(_funcDict)
                            del _funcDict["funcName"]
                        _lineIdx = _lineAndCharIdx[0]
                else:
                    self.raiseError(
                        pyUtils.getCurrentRunningFunctionName(),
                        " : not close"
                    )
            else:
                if _line.lstrip().startswith("class") or _line.find(" class ") >= 0:
                    print("Class Warning : " + str(_line))
        return _classList

    def getFuncList(self, lines_: list, startIdx_: int, endIdx_: int):
        _funcDictList = []  # 方法
        for _lineIdx in range(startIdx_, endIdx_):
            _line = lines_[_lineIdx]
            _funcRegStr = self.belongToService.funcRegStr
            _funcReg = re.search(_funcRegStr, _line)

            if not _funcReg:  # 可能是自己使用自己，或者继承他人的构造器
                _funcReg = re.search(
                    r'^([=\.\[\] ,<>a-zA-Z0-9_\t]*)\s+([a-zA-Z0-9_]+)\s*\(\s*([^\)]*)\s*\)\s*:\s*(base|this).*\{',
                    _line
                )

            if _funcReg:
                _prefix = _funcReg.group(1)
                _funcName = _funcReg.group(2)
                _parameter = _funcReg.group(3)
                if not _funcName in self.belongToService.notFuncNameList:
                    _isFunc = False
                    # print(_funcReg.group(0))
                    # print('_prefix    = ' + str(_prefix))
                    # print('_funcName  = ' + str(_funcName))
                    # print('_parameter = ' + str(_parameter))
                    _prefix = strUtils.spacesReplaceToSpace(_prefix)
                    _parameter = strUtils.spacesReplaceToSpace(_parameter)
                    if _prefix.strip() == "":
                        # 没有开放域指定的构造 是类构造器
                        # TypeParser(string fullname) {
                        _isFunc = True
                    if not _isFunc:
                        _prefixArr = _prefix.split(" ")
                        if len(_prefixArr) == 1:
                            # 类名前是开放域指定 是类构造器
                            # public JSONLazyCreator(JSONNode aNode) {
                            if _prefixArr[0] in self.belongToService.funcTypeList:
                                _isFunc = True
                        if not _isFunc:
                            if _prefix.endswith("new"):  # 创建语句 new
                                continue
                            elif _prefix.find("IEnumerable") > 0:  # 协程返回 IEnumerable<Type>，不要获取return，可能会被 yield
                                continue
                            elif _prefix.endswith("IEnumerator"):  # 协程返回 IEnumerator，不要获取return，可能会被 yield
                                continue
                            elif len(_prefixArr) >= 2 and _prefixArr[len(_prefixArr) - 2] == "new":  # 覆盖方法
                                _isFunc = True
                            else:
                                _isFunc = True

                    # 是方法的话，进行记录
                    if _isFunc:
                        _funcDict = {}
                        _funcDict["funcName"] = _funcName
                        _funcDict["parameters"] = self.getPrintableParameter(_parameter)
                        # 不找结束，只找起始
                        _funcDict["startLineIdx"] = _lineIdx
                        # 找大括号结束的位置
                        _lineAndCharIdx = self.belongToService.curlyBraces.getCloseCurlyBraces(_lineIdx + 1, lines_)
                        if not _lineAndCharIdx == None:
                            _closeLine = lines_[_lineAndCharIdx[0]]
                            if not _closeLine.strip() == "}" and not _closeLine.strip() == "};":
                                print("func Warning : " + str(_closeLine))
                            # # 记录function的始末位置
                            _funcDict["endLineIdx"] = _lineAndCharIdx[0]
                            _funcDict["endLineCharIdx"] = _lineAndCharIdx[1]
                            # _funcDict["returnLineIdxList"]
                            _lineIdx = _lineAndCharIdx[0]
                        else:
                            self.raiseError(
                                pyUtils.getCurrentRunningFunctionName(), " : not close"
                            )
                        _funcDictList.append(_funcDict)
        return _funcDictList

    def getPrintableParameter(self, parameters_: str):
        _parameterReg = r'(,*)(out)?\s*(uint|string|int|bool|float)\s+([a-zA-Z0-9_]+)\s*'
        matches = re.finditer(_parameterReg, parameters_, re.MULTILINE)
        _parameterList = []
        for matchNum, match in enumerate(matches, start=1):
            if not match.group(2) == "out":
                _parameterName = match.group(4)
                if match.group(3) == "string":
                    _parameterList.append(
                        _parameterName + " : \"+(" + _parameterName + "==null?\"\":" + _parameterName + ".ToString())+\""
                    )
                else:
                    _parameterList.append(_parameterName + " : \"+" + _parameterName + ".ToString()+\"")
        if len(_parameterList) > 0:
            return "\" ( " + " , ".join(_parameterList) + " )\""
        else:
            return ""
