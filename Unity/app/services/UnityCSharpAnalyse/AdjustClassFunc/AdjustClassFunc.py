#!/usr/bin/env python3
# Created by jiasy at 2020/5/15
from base.supports.Base.BaseInService import BaseInService
from utils import *
import re


class AdjustClassFunc(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(AdjustClassFunc, self).create()

    def destory(self):
        super(AdjustClassFunc, self).destory()

    # 整理 类创建 和 方法 的书写格式
    def adjustClassFuncVariableLineFolder(self, srcFolderPath_: str, targetFolderPath_: str):
        _csCodeFolder = fileUtils.getPath(srcFolderPath_, "")
        _filePathList = folderUtils.getFileListInFolder(_csCodeFolder, [".cs"])
        for _path in _filePathList:
            print(_path)
            _content = self.adjustClassFuncVariableLineFile(_path)
            _targetFilePath = targetFolderPath_ + _path.split(srcFolderPath_).pop()
            fileUtils.writeFileWithStr(_targetFilePath, _content)

    def adjustClassFuncVariableLineFile(self, path_: str):
        _content = fileUtils.readFromFile(path_)
        _content = self.adjustCurlyBracesBlank(_content)
        _content = self.adjustReturnInOneLine(_content)
        _content = self.adjustClassFuncInOneLine(_content)
        _content = self.adjustClassLineFile(_content)
        _content = self.adjustFuncLineFile(_content)
        _content = self.adjustAnonymous(_content)  # 匿名函数
        _content = self.adjustDelegateWrite(_content)  # delegate的写法调整
        _content = self.adjustCommaSymbol(_content)  # 逗号写法调整
        # return 两面的多空格全部变成一个
        _content = re.sub(r' +return +', ' return ', _content)
        # self.checkContent(_content)
        return _content

    def adjustCommaSymbol(self, connect_):
        _content = connect_
        _commaSymbolReg = r'([\w>])\s*,\s*([\w])'
        matches = re.finditer(_commaSymbolReg, _content, re.MULTILINE)
        # 逗号两侧 -> 固定左右个一个空格
        for matchNum, match in enumerate(matches, start=1):
            _targetCode = match.group(1) + " , " + match.group(2)
            _content = _content.replace(match.group(0), _targetCode)
        return _content

    def checkContent(self, content_):
        _content = content_
        _lines = _content.split("\n")
        _count = 0
        for _line in _lines:
            _count += 1
            _oneLineReturnReg = re.search(r';[ \t]*return ', _line)
            if _oneLineReturnReg:
                self.raiseError(
                    pyUtils.getCurrentRunningFunctionName(),
                    "有一行内多个逻辑，其中有return的情况发生 : " + _oneLineReturnReg.group(0)
                )
            _returnNotAtStart = re.search(r'^(.*[^ ^\t]) return ', _line)
            if _returnNotAtStart:
                _prefix = _returnNotAtStart.group(1)
                if re.search(r'case .*:', _prefix):
                    self.raiseError(
                        pyUtils.getCurrentRunningFunctionName(),
                        "return 并不是新行起始 case : " + _returnNotAtStart.group(0)
                    )
                elif not _prefix.endswith("yield"):
                    if not (_prefix.find('\'') > 0 or _prefix.find('"') > 0):
                        self.raiseError(
                            pyUtils.getCurrentRunningFunctionName(),
                            "return 并不是新行起始 : " + _returnNotAtStart.group(0)
                        )

    # 调整一些基本写法
    def adjustDelegateWrite(self, content_: str):
        _content = content_
        # 没有参数的 delegate{ ->  delegate(){
        _content = re.sub(r'delegate\s*\{', 'delegate(){', _content)
        # delegate ( - > delegate(
        _content = re.sub(r'delegate\s*\(', 'delegate(', _content)
        return _content

    # 调整匿名函数
    def adjustAnonymous(self, content_: str):
        _content = content_
        _oneLineReg = r'([a-zA-Z0-9_]+)\s*=>\s*\{'
        matches = re.finditer(_oneLineReg, _content, re.MULTILINE)
        # x => { -> (x)=>{
        for matchNum, match in enumerate(matches, start=1):
            _targetCode = "(" + match.group(1) + ")=>{"
            _content = _content.replace(match.group(0), _targetCode)
        return _content

    # 调整大括号
    def adjustCurlyBracesBlank(self, content_: str):
        def removeFuncBlank(reg_):
            # x ( -> x( / x { -> x{ / ) return -> )return
            _str = reg_.group()
            return re.sub(r'\s+', "", _str)

        # 缓存内容
        _content = content_
        # 查找到所有的 x ( ，然后变换这个格式
        _content = re.sub(r'([a-zA-Z0-9_])[ \t]*\(', removeFuncBlank, _content)
        # 查找到所有的 x ( ，然后变换这个格式
        _content = re.sub(r'([a-zA-Z0-9_])[ \t]*\{', removeFuncBlank, _content)
        # 查找到所有的 ) return ，然后变换这个格式
        _content = re.sub(r'\)\s+return', removeFuncBlank, _content)
        # 查找到所有的 ) {，然后变换成 ){
        _content = re.sub(r'\)\s*\{', '){', _content)
        # 查找到所有 { return，然后变成 {return
        _content = re.sub(r'\{[ \t]*return\s+', '{return ', _content)
        return _content

    def adjustReturnInOneLine(self, content_: str):
        _content = content_
        _oneLineReg = r'^(.*)\{[ \t]*return\s+(.*?)\s*;*[ \t]*\}([ \t]*;*)(.*)$'
        matches = re.finditer(_oneLineReg, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            _returnContent = match.group(2)
            _suffix = match.group(3)
            _suffixAfter = match.group(4)
            _blank = len(_prefix) * " "
            _targetCode = _prefix + "{" + "\n"
            _targetCode += _blank + "    return " + _returnContent + ";" + "\n"
            _targetCode += _blank + "}" + _suffix + "\n"
            _targetCode += _blank + _suffixAfter
            _content = _content.replace(match.group(0), _targetCode)
        return _content

    # 方法一行的拆分开,
    def adjustClassFuncInOneLine(self, content_: str):
        _content = content_
        _oneLineReg = r'^(.*)\s+([a-zA-Z0-9_]+)\s*\(\s*([^\)]*)\s*\)\s*\{(.*?)\}([ \t]*;*)'
        matches = re.finditer(_oneLineReg, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            _funcName = match.group(2)
            _parameters = match.group(3)
            _funcContent = match.group(4)
            _suffix = match.group(5)
            # 前半部分中存在 引号，有可能后半部分在引号中，所以，不拆分当前行。[简单的直接认为]
            if _prefix.find("\'") >= 0 or _prefix.find('"') >= 0 or _prefix.find('@"') >= 0 or _prefix.endswith("new"):
                return _content
            _blank = ""
            _blankGetReg = re.search(r'(\s+)([a-zA-Z0-9_]+)', _prefix)
            if _blankGetReg:
                _blank = _blankGetReg.group(1)
            _targetCode = _prefix + " " + _funcName + "(" + _parameters + "){" + "\n"
            _funcContent = _funcContent.strip()
            _targetCode += _blank + _funcContent + "\n"
            _targetCode += _blank + "}" + _suffix
            _content = _content.replace(match.group(0), _targetCode)
        return _content

    # 继承的多行代码，合并成一行
    def adjustClassLineFile(self, content_: str):
        _content = content_
        _extendClassCreatorRegex = r'^(.*)\s+([a-zA-Z0-9_]+)\s*\(\s*(.*?)\s*\)\s*:\s*(base|this)\s*\((.*)\)\s*\{'
        matches = re.finditer(_extendClassCreatorRegex, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            _className = match.group(2)
            _parameters = match.group(3)
            _parameters = self.dealParameters(_parameters)
            _baseOrThis = match.group(4)
            _superParameters = match.group(5)
            _superParameters = self.dealParameters(_superParameters)
            _targetCode = _prefix + " " + _className + "(" + _parameters + "):" + _baseOrThis + "(" + _superParameters + "){"
            _content = _content.replace(match.group(0), _targetCode)
        return _content

    # 方法合并成一行
    def adjustFuncLineFile(self, content_: str):
        _content = content_
        _funcRegex = self.belongToService.funcRegStr
        matches = re.finditer(_funcRegex, _content, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            _prefix = match.group(1)
            _funcName = match.group(2)
            _parameters = match.group(3)
            _parameters = self.dealParameters(_parameters)
            if not _funcName in self.belongToService.notFuncNameList:
                _targetCode = _prefix + " " + _funcName + "(" + _parameters + "){"
                _content = _content.replace(match.group(0), _targetCode)
        return _content

    def dealParameters(self, parameters_: str):
        _parameters = parameters_.split("\n")
        _newParameters = []
        for _parameter in _parameters:
            _newParameters.append(_parameter.strip())
        return "".join(_newParameters)
