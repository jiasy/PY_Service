#!/usr/bin/env python3
# Created by jiasy at 2020/9/27

from Excel.ExcelBaseInService import ExcelBaseInService
import os
import sys
from pathlib import Path
from utils import sysUtils
from utils import cmdUtils
from utils import pyUtils
import git


class GitBaseOperate(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "CheckOut": {
                "gitFolderPath": "本地路径",
                "branch": "分支名称",
                "path": "路径，不填写为全部下载",
            },
            "ReCreateTag": {
                "gitFolderPath": "本地路径",
                "tag": "tag名",
            },
            #         changed
            #             修改 但未 add:    需要把指定文件在工作区的修改全部撤销
            # 　　　　　　　　　　git checkout -- <filename>   (注意: --后面要空一格)
            #         added
            #             add 但未 commit:　需要把暂存区的修改撤销掉（unstage），重新放回工作区
            # 　　　　　　　　　　 git reset <filename>
            # 　　　　　　　　　　 git reset HEAD <filename>
            #         committed
            #             add 且已 commit 但未 push:　需要版本切换
            #                  git reset --hard <commitID>
            "Undo": {
                "type": "类型，支持changed/added/committed",
            },
        }

    def create(self):
        super(GitBaseOperate, self).create()

    def destory(self):
        super(GitBaseOperate, self).destory()

    def ReCreateTag(self, dParameters_):
        _gitFolderPath = sysUtils.folderPathFixEnd(dParameters_["gitFolderPath"])
        _tag = dParameters_["tag"]
        _repo = git.Repo.init(_gitFolderPath)
        if _tag in _repo.tags:
            _repo.delete_tag(_tag)  # 删除已有的
        _repo.create_tag(_tag)  # 创建新的

    def CheckOut(self, dParameters_):
        _gitFolderPath = sysUtils.folderPathFixEnd(dParameters_["gitFolderPath"])
        _branch = dParameters_["branch"]
        _path = dParameters_["path"]

        # 本地没有的时候，将远程的迁出到本地。本地和远端同名
        _localBranchName = _branch.split("/")[-1]  # 本地该叫什么名
        _branchStrList = cmdUtils.doStrAsCmd('git branch', _gitFolderPath, True)  # 输出本地有什么
        _localBranchNameList = []
        _currentLocalBranchName = ""
        for _i in range(len(_branchStrList)):
            _currentBranchName = _branchStrList[_i][2:]
            _localBranchNameList.append(_currentBranchName)  # 记录本地名列表
            if _branchStrList[_i].startswith("* "):  # 当前所在那个本地分支
                _currentLocalBranchName = _currentBranchName

        # 不在指定名称分支内
        if not _currentLocalBranchName == _localBranchName:
            # 本地没有这个名称的分支
            if not _localBranchName in _localBranchNameList:
                # 在当前git所在目录，检出分支，指定其名称
                cmdUtils.doStrAsCmd("git checkout " + _branch + " -b " + _localBranchName, _gitFolderPath, True)
            else:
                # 本地，有分支，只需要检出
                cmdUtils.doStrAsCmd("git checkout " + _localBranchName, _gitFolderPath, True)

        # 路径整理
        if _path.startswith("\\") or _path.startswith("/"):
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "path 不能以 \\ 或 / 开头")
        _path = str(Path(_path))  # "" 会被转换成 "."
        if _path == ".":
            cmdUtils.doStrAsCmd('git checkout .', _gitFolderPath, True)
        else:
            cmdUtils.doStrAsCmd('git checkout -- ' + _path, _gitFolderPath, True)


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    # _functionName = "CheckOut"
    # _parameterDict = {  # 所需参数
    #     "gitFolderPath": "/Volumes/18604037792/develop/ShunYuan/protocol_farm/",
    #     "branch": "remotes/origin/2020年5月27日强更线上版",
    #     "path": "server/readme.txt",
    #     # "path": "server",
    # }

    _functionName = "ReCreateTag"
    _parameterDict = {  # 所需参数
        "gitFolderPath": "/Volumes/18604037792/develop/ShunYuan/protocol_farm/",
        "tag": "publish_1124",
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
