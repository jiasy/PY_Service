#!/usr/bin/env python3
# Created by jiasy at 2020/5/24
from base.supports.Base.BaseInService import BaseInService
from utils import *
import subprocess
import re


class DrawClassRelation(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(DrawClassRelation, self).create()

    def destory(self):
        super(DrawClassRelation, self).destory()

    def isInterface(self, className_):
        if re.search(r'^I[A-Z]{1}', className_):
            return True
        elif className_.find("_") > 0:
            if re.search(r'^I[A-Z]{1}', className_.split("_").pop()):
                return True
        else:
            return False

    # 画类结构，不带文件夹
    def drawClassRelationWithOutFolderStructure(self,
                                                fileClassFuncDict_: dict,
                                                targetFolderPath_: str,
                                                onlyIncludeExtends_: bool
                                                ):
        _classAllList = []
        for _fileShortName in fileClassFuncDict_.keys():
            _fileClassDict = fileClassFuncDict_[_fileShortName]
            for _className in _fileClassDict.keys():
                _classDict = _fileClassDict[_className]
                _extendsFromClassList = _classDict["extendsFrom"]  # 全局类中包含继承
                _className = _className.replace(".", "_")
                if onlyIncludeExtends_:  # 只有继承关系的类才要显示的话
                    if not _className in _classAllList and (len(_extendsFromClassList) > 0):  # 判断是否继承了其他类
                        _classAllList.append(_className)
                else:
                    if not _className in _classAllList:  # 只要没记录过就记录
                        _classAllList.append(_className)
                for _extendsFromClass in _extendsFromClassList:  # 被继承类也要创建节点
                    _extendsFromClass = _extendsFromClass.replace(".", "_")
                    if not _extendsFromClass in _classAllList:
                        _classAllList.append(_extendsFromClass)
        _classNodesStr = ""
        for _class in _classAllList:
            if self.isInterface(_class):
                _classNodesStr += _class + "    [label = \"o - " + _class + "\"]" + "\n"
            else:
                _classNodesStr += _class + "    [label = \"" + _class + "\"]" + "\n"

        _extendsStr = ""
        for _fileShortName in fileClassFuncDict_.keys():
            _fileClassDict = fileClassFuncDict_[_fileShortName]
            for _className in _fileClassDict.keys():
                _classDict = _fileClassDict[_className]
                _className = _className.replace(".", "_")
                _extendsFromClassList = _classDict["extendsFrom"]
                for _extendsFromClass in _extendsFromClassList:
                    _extendsFromClass = _extendsFromClass.replace(".", "_")
                    if self.isInterface(_extendsFromClass):
                        _extendsStr = _extendsStr + \
                                      _className + \
                                      " -> " + \
                                      _extendsFromClass + \
                                      "  [style=\"dashed\"]" + \
                                      "\n"

                    else:
                        _extendsStr = _extendsStr + \
                                      _className + \
                                      " -> " + \
                                      _extendsFromClass + \
                                      "\n"
        if onlyIncludeExtends_:
            self.writeDotAndCreatePng(targetFolderPath_, _classNodesStr, _extendsStr, "classRelation_Only_Extends")
        else:
            self.writeDotAndCreatePng(targetFolderPath_, _classNodesStr, _extendsStr, "classRelation")

    # 画类结构，带文件夹
    def drawClassRelation(self,fileClassFuncDict_: dict, targetFolderPath_: str):
        _classAllList = []
        _folderDict = {}
        for _fileShortName in fileClassFuncDict_.keys():
            _fileClassDict = fileClassFuncDict_[_fileShortName]
            _folderSortName = None
            if _fileShortName.find("/"):
                _folderSortNameArr = _fileShortName.split("/")
                _folderSortNameArr.pop()
                _folderSortName = "/".join(_folderSortNameArr)
                if not _folderSortName in _folderDict.keys():
                    _folderDict[_folderSortName] = []
            for _className in _fileClassDict.keys():
                _classDict = _fileClassDict[_className]
                _className = _className.replace(".", "_")
                if not _className in _classAllList:
                    _classAllList.append(_className)
                if _folderSortName != None:
                    _folderDict[_folderSortName].append(_className)
                _extendsFromClassList = _classDict["extendsFrom"]  # 全局类中包含继承
                for _extendsFromClass in _extendsFromClassList:
                    _extendsFromClass = _extendsFromClass.replace(".", "_")
                    if not _extendsFromClass in _classAllList:
                        _classAllList.append(_extendsFromClass)

        _classAllList = list(set(_classAllList))  # 去重
        _classNodesStr = ""
        for _folderSortName in _folderDict.keys():
            _classNodesInFolderStr = ""
            _classInFolderList = _folderDict[_folderSortName]
            _classInFolderList = list(set(_classInFolderList))  # 去重
            for _class in _classInFolderList:
                # 如果类已经输出过了，就从全局内去掉。
                if _class in _classAllList:
                    _classAllList.remove(_class)
                if self.isInterface(_class):
                    _classNodesInFolderStr += _class + "    [label = \"o - " + _class + "\"]" + "\n"
                else:
                    _classNodesInFolderStr += _class + "    [label = \"" + _class + "\"]" + "\n"
            _classNodesStr += 'subgraph "cluster_' + _folderSortName + '" { label="' + _folderSortName + '"; \n' + _classNodesInFolderStr + ' };\n'
        # 其他未在文件夹内的
        for _class in _classAllList:
            if self.isInterface(_class):
                _classNodesStr += _class + "    [label = \"o - " + _class + "\"]" + "\n"
            else:
                _classNodesStr += _class + "    [label = \"" + _class + "\"]" + "\n"

        _extendsStrList = []
        for _fileShortName in fileClassFuncDict_.keys():
            _fileClassDict = fileClassFuncDict_[_fileShortName]
            for _className in _fileClassDict.keys():
                _classDict = _fileClassDict[_className]
                _extendsFromClassList = _classDict["extendsFrom"]
                for _extendsFromClass in _extendsFromClassList:
                    if self.isInterface(_extendsFromClass):
                        _extendsStrList.append(
                            _className.replace(".", "_") +
                            " -> " +
                            _extendsFromClass.replace(".", "_") +
                            "  [style=\"dashed\"]" +
                            "\n"
                        )
                    else:
                        _extendsStrList.append(
                            _className.replace(".", "_") + " -> " +
                            _extendsFromClass.replace(".", "_") +
                            "\n"
                        )

        _extendsStrList = list(set(_extendsStrList))
        _extendsStr = "".join(_extendsStrList)
        self.writeDotAndCreatePng(targetFolderPath_, _classNodesStr, _extendsStr, "classRelationWithFolderStructure")

    def writeDotAndCreatePng(self, targetFolderPath_: str, nodesStr_: str, relationStr_: str, dotFileName_: str):
        # '''
        # rankdir = LR;
        # splines = polyline;
        # size="50,50"; ratio=fill; node[fontsize=24];
        # '''
        _targetStr = '''
digraph classRelation{{
    rankdir = LR; // 箭头从下到上
    node [shape = "record", fontname = "Consolas" , fontsize = 24]// 默认方形
    edge [arrowhead = "empty", fontname = "Consolas"]// 默认空箭头
    size="50,100"; ratio=fill;
{0}
{1}
}}
'''.format(nodesStr_, relationStr_)
        _dotFilePath = targetFolderPath_ + dotFileName_ + ".dot"
        fileUtils.writeFileWithStr(_dotFilePath, _targetStr)
        _cmd = 'dot ' + dotFileName_ + '.dot -T png -o ' + dotFileName_ + '.png'
        print(_cmd)
        subprocess.Popen(_cmd, shell=True, cwd=targetFolderPath_)
