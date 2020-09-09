#!/usr/bin/env python3
# Created by jiasy at 2020/4/21
from base.supports.Base.BaseInService import BaseInService
from utils import folderUtils
from utils import fileUtils
from utils import pyUtils
import re
import subprocess


# 解析工程，代码之间的相互引用关系图
class PrefabCombineJSAnalyse(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self._jsFolder = "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/scripts/"
        # 对应prefab的js文件
        self._jsComponentFileShortNameList = []
        # 导出模块的js文件
        self._jsModuleExportsFileShortNameList = []
        # 所有js文件
        self._jsAllShortNameList = []
        # 所有 require 的 js
        self._requireDict = {}

    def create(self):
        super(PrefabCombineJSAnalyse, self).create()

    def destory(self):
        super(PrefabCombineJSAnalyse, self).destory()

    # 通过justName 获取 shortName
    def getMoudleExportShortNameByJustName(self, justName_):
        for _shortName in self._jsModuleExportsFileShortNameList:
            if (_shortName.find("/") >= 0 and _shortName.endswith("/" + justName_ + ".js")) or \
                    (_shortName.find("/") < 0 and _shortName == justName_ + ".js"):
                return _shortName
        return None

    # 所有的js短名和js引用关系
    def anaylseShortJsNameAndRequireRelation(self):
        _filePathDict = folderUtils.getFilePathKeyValue(self._jsFolder, [".js"])
        for _, _filePath in _filePathDict.items():
            _jsFileShortName = _filePath.split(self._jsFolder)[1]
            self._requireDict[_jsFileShortName] = []
            if not (_jsFileShortName in self._jsAllShortNameList):
                self._jsAllShortNameList.append(_jsFileShortName)
            # 内容中识别 require
            _content = fileUtils.readFromFile(_filePath)
            regex = r"var\s*([0-9a-z-A-Z_\.]+)\s*=\s*require\(\s*\"([0-9a-z-A-Z_\.]+)\"\s*\)"
            matches = re.finditer(regex, _content, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                _localName = match.group(1)  # 代码中的名称
                _fileName = match.group(2)  # 引用名称
                _lines = _content.split("\n")
                _isFind = False
                for _line in _lines:
                    # 注释的前半截
                    _line = _line.split("//")[0]
                    # 在不是require的行中搜索
                    if not re.search(r'require\(\s*\"([0-9a-z-A-Z_\.]+)\"\s*\)', _line) and _line.find(
                            "module.exports") < 0:
                        if (re.search(r'[\s\(\[=\!\+\-\*/\']' + _localName + '[\,\.\s=\)\]\+\-\*/\'\[]', _line)):
                            _isFind = True
                            break
                if _isFind:
                    self._requireDict[_jsFileShortName].append(_fileName)
                else:
                    print(_filePath)
                    print(_fileName)
                    self.raiseError(pyUtils.getCurrentRunningFunctionName(), "文件引用了类，但是没有使用过")

    # 将js关系显示成图
    def toDotDict(self, dotPicFolder_: str):

        _relationFileColorDict = {}
        _relationFolderColorDict = {}
        _colorCurrentIdx = -1

        _colorList = [
            "blue",
            "brown",
            "orange",
            "cadetblue4",
            "chartreuse4",
            "chocolate4",
            "dodgerblue4",
            "red",
            "purple3",
            "green",
            "crimson",
            "lightsteelblue4",
            "aquamarine4",
        ]

        _filterFolderList = [
            "Message",
            "WeChat",
            "Common"
        ]
        _filterFileList = []

        _foldAndFileDict = {}
        for _key in self._jsAllShortNameList:
            _keyArr = _key.split("/")
            if len(_keyArr) != 2:
                continue
            # 文件夹 ，文件
            _folder = _keyArr[0]
            _file = _keyArr[1]
            # 跳过某些文件夹
            if _folder in _filterFolderList:
                if not _file in _filterFileList:
                    _filterFileList.append(_file)
                continue
            else:
                if not (_folder in _foldAndFileDict):
                    _relationFolderColorDict[_folder] = _colorList[_colorCurrentIdx]
                    _foldAndFileDict[_folder] = []
                    _colorCurrentIdx += 1
                    # 同一个文件夹内都是同色
                    if _colorCurrentIdx == len(_colorList):
                        _colorCurrentIdx = 0
                if not (_file in _foldAndFileDict[_folder]):
                    _foldAndFileDict[_folder].append(_file)
                    _relationFileColorDict[_file] = _colorList[_colorCurrentIdx - 1]

        _mapName = "jsRelation"
        # 构成 dot 文件
        _dotStr = "digraph " + _mapName + " {\n"
        _dotStr += '  rankdir = LR;\n'
        # _dotStr += '  splines = polyline;\n'
        _dotStr += 'size="50,50"; ratio=fill; node[fontsize=24];\n'

        for _folder, _fileList in _foldAndFileDict.items():
            _fileListStr = ""
            for _baseName in _fileList:
                _fileListStr += '"' + _baseName + '" [shape = note, color = "' + _relationFolderColorDict[
                    _folder] + '", fontcolor = "' + _relationFolderColorDict[_folder] + '", fontcolor = "white"];'
            _dotStr += 'subgraph "cluster_' + _folder + '" { node [style=filled]; label="' + _folder + '"; ' + _fileListStr + ' };\n'

        for _file, _requireList in self._requireDict.items():
            _nameArr = _file.split("/")
            _folder = _nameArr[0]
            if _folder in _filterFolderList:
                continue
            _baseName = _nameArr.pop()
            for _require in _requireList:
                _requireJs = _require + ".js"
                if not _requireJs in _filterFileList:
                    if _requireJs in _relationFileColorDict:
                        _color = _relationFileColorDict[_requireJs]
                        _dotStr += '  "' + _baseName + '" -> "' + _requireJs + '" [color = ' + _color + '];\n'
                    else:
                        _dotStr += '  "' + _baseName + '" -> "' + _requireJs + '";\n'
        _dotStr += "}\n"

        _dotFilePath = dotPicFolder_ + _mapName + ".dot"
        fileUtils.writeFileWithStr(_dotFilePath, _dotStr)
        _cmd = 'dot ' + _mapName + '.dot -T png -o ' + _mapName + '.png'
        print(_cmd)
        subprocess.Popen(_cmd, shell=True, cwd=dotPicFolder_)

    # 解析 Prefab 上挂载 的 Component
    def analysePrefab(self):
        _filePathDict = folderUtils.getFilePathKeyValue(self._jsFolder, [".js"])
        for _, _filePath in _filePathDict.items():
            self.analysePrefabJS(_filePath)

    def analysePrefabJS(self, jsPath_: str):
        _content = fileUtils.readFromFile(jsPath_)
        _propertiesReg = re.search(r'properties\s*:\s*{', _content)
        if _propertiesReg:
            _jsFileShortName = jsPath_.split(self._jsFolder)[1]
            if not (_jsFileShortName in self._jsComponentFileShortNameList):
                self._jsComponentFileShortNameList.append(_jsFileShortName)

            # 为Component 添加 className 属性
            # _fileName = fileUtils.justName(jsPath_)
            # _content = re.sub(
            #     r"( *)properties\s*:\s*{",
            #     r'\1properties: {\n\1  className: \'' + _fileName + '\',',
            #     _content)
            # fileUtils.writeFileWithStr(jsPath_, _content)

    # 解析 moudle.exports
    def analyseMoudleExports(self):
        _filePathDict = folderUtils.getFilePathKeyValue(self._jsFolder, [".js"])
        for _, _filePath in _filePathDict.items():
            self.analyseMoudleExportsJS(_filePath)

    def analyseMoudleExportsJS(self, jsPath_: str):
        _content = fileUtils.readFromFile(jsPath_)
        _moudleNameReg = re.search(r'module\.exports\s*=\s*([0-9a-z-A-Z_]+)\s*', _content)
        if _moudleNameReg:
            _jsFileShortName = jsPath_.split(self._jsFolder)[1]
            if not (_jsFileShortName in self._jsModuleExportsFileShortNameList):
                self._jsModuleExportsFileShortNameList.append(_jsFileShortName)

        _moudleNameReg = re.search(r'module\.exports\s*=\s*{', _content)
        if _moudleNameReg:
            _jsFileShortName = jsPath_.split(self._jsFolder)[1]
            if not (_jsFileShortName in self._jsModuleExportsFileShortNameList):
                self._jsModuleExportsFileShortNameList.append(_jsFileShortName)
