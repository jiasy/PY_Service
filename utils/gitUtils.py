# !/usr/bin/env python3
from git import Repo  # 导入repo模块
import utils.printUtils
import utils.strUtils
import functools


# 获取包含 给定字符串的 Tag 列表
# _repo = gitUtils.getRepo(本地工程路径)
def getRepo(localFolderPath_):
    return Repo.init(localFolderPath_)


def showRepoInfo(repo_):
    print("所有的分支 : ")
    utils.printUtils.printList(repo_.branches, "  ")
    print("所有未加入版本的文件 : ")
    utils.printUtils.printList(repo_.untracked_files, "  ")
    print("当前活动分支 : " + str(repo_.active_branch))
    print("当前活动分支 : " + str(repo_.head.reference))
    print("运程库 : " + str(repo_.remotes.origin))
    print("TAGs : ")
    utils.printUtils.printList(repo_.tags, "  ")


def getCurrentBiggestVersion(repo_):
    # 获取当前满足版本格式的Tag中最大的tag号
    _tagStrList = [str(_tagName) for _tagName in repo_.tags if utils.strUtils.isVersionStr(str(_tagName))]
    _tagStrList = sorted(_tagStrList, key=functools.cmp_to_key(utils.strUtils.versionCompare), reverse=True)
    return _tagStrList[0]


def getNextVersion(currentVersion_: str):
    _tagIntList = [int(_tarStr) for _tarStr in currentVersion_.split(".")]
    _tagIntList[-1] = _tagIntList[-1] + 1
    _nextTar = ".".join([str(_tarInt) for _tarInt in _tagIntList])
    return _nextTar


# 创建一个标签
def createTag(repo_, tarName_):
    repo_.create_tag(tarName_)
