#!/usr/bin/env python3
import json
import os
import shutil
import utils.sysUtils
import utils.folderUtils


# 文件夹 同结构拷贝
# fileCopyUtils.copyFilesInFolderTo([".jpg",".png"],"原路径","目标路径","include",false) # 只拷贝后缀列表中的
# fileCopyUtils.copyFilesInFolderTo([".meta"],"原路径","目标路径","exclude",false)
def copyFilesInFolderTo(suffixList_: list, src_root: str, dst_root: str, type_: str = "include", log_: bool = False):
    _configObject = {}
    _configObject["from"] = ""
    _configObject["to"] = ""
    _configObject[type_] = []
    for _i in range(len(suffixList_)):
        _suffix = suffixList_[_i]
        _configObject[type_].append("*" + _suffix + "$F")
    copyFilesWithConfig([_configObject], src_root, dst_root, log_)


# 根据配置结构拷贝
def copyFilesWithConfig(config_, srcRoot_, dstRoot_, log_):
    for _i in range(len(config_)):
        copyFilesWithConfigSingle(config_[_i], srcRoot_, dstRoot_, log_)


# 拷贝文件---------------------------------------------------------------------------------------
def copyFilesInDir(src_, dst_, log_):
    for _item in os.listdir(src_):
        _path = os.path.join(src_, _item)
        if os.path.isfile(_path):
            _copyDst = utils.sysUtils.folderPathFixEnd(dst_)
            shutil.copy(_path, _copyDst)
            if log_:
                print("---File Copy---")
                print("		src : " + _path)
                print("		tar : " + _copyDst)
        if os.path.isdir(_path):
            _newDst = os.path.join(dst_, _item)
            utils.folderUtils.makeSureDirIsExists(_newDst)
            copyFilesInDir(_path, _newDst, log_)


def copyFilesWithConfigSingle(config_, srcRoot_, dstRoot_, log_):
    _srcDir = config_["from"]
    _dstDir = config_["to"]
    _srcDir = os.path.join(srcRoot_, _srcDir)
    _dstDir = os.path.join(dstRoot_, _dstDir)
    _includeRules = None
    if "include" in config_:
        _includeRules = config_["include"]
        _includeRules = convert_rules(_includeRules)

    _excludeRules = None
    if "exclude" in config_:
        _excludeRules = config_["exclude"]
        _excludeRules = convert_rules(_excludeRules)

    copyFilesWithRules(
        _srcDir, _srcDir, _dstDir, log_, _includeRules, _excludeRules)


def copyFilesWithRules(srcRootDir_, src_, dst_, log_, include_=None, exclude_=None):
    if os.path.isfile(src_):
        _copySrc = src_
        _copyDst = utils.sysUtils.folderPathFixEnd(dst_)
        utils.folderUtils.makeSureDirIsExists(_copyDst)
        shutil.copy(_copySrc, _copyDst)
        return

    if (include_ is None) and (exclude_ is None):
        utils.folderUtils.makeSureDirIsExists(dst_)
        copyFilesInDir(src_, dst_, log_)
    elif (include_ is not None):
        # have include
        for _name in os.listdir(src_):
            _absPath = os.path.join(src_, _name)
            _relPath = os.path.relpath(_absPath, srcRootDir_)
            if os.path.isdir(_absPath):
                _subDst = os.path.join(dst_, _name)
                copyFilesWithRules(
                    srcRootDir_,
                    _absPath,
                    _subDst,
                    log_,
                    include_=include_
                )
            elif os.path.isfile(_absPath):
                if _in_rules(_relPath, include_):
                    _copyDst = utils.sysUtils.folderPathFixEnd(dst_)
                    utils.folderUtils.makeSureDirIsExists(_copyDst)
                    shutil.copy(_absPath, _copyDst)
    elif (exclude_ is not None):
        # have exclude
        for _name in os.listdir(src_):
            _absPath = os.path.join(src_, _name)
            _relPath = os.path.relpath(_absPath, srcRootDir_)
            if os.path.isdir(_absPath):
                _subDst = os.path.join(dst_, _name)
                copyFilesWithRules(srcRootDir_, _absPath, _subDst, log_, exclude_=exclude_)
            elif os.path.isfile(_absPath):
                if not _in_rules(_relPath, exclude_):
                    _copyDst = utils.sysUtils.folderPathFixEnd(dst_)
                    utils.folderUtils.makeSureDirIsExists(_copyDst)
                    shutil.copy(_absPath, _copyDst)


def _in_rules(relPath_, rules_):
    import re
    _ret = False
    _pathStr = relPath_.replace("\\", "/")
    for _rule in rules_:
        if re.match(_rule, _pathStr):
            _ret = True
    return _ret


def convert_rules(rules):
    _retRules = []
    for _rule in rules:
        _ret = _rule.replace('.', '\\.')
        _ret = _ret.replace('*', '.*')
        _ret = "%s" % _ret
        _retRules.append(_ret)
    return _retRules


if __name__ == "__main__":
    # 拷贝图片
    copyFilesInFolderTo(
        [".jpg", ".png"],
        "/Volumes/Files/develop/loho/mini-game/resources/",
        "/Volumes/Files/develop/loho/mini-game/miniclient/assets/resources/"
    )
