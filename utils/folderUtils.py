# !/usr/bin/env python3
import os
import utils.fileUtils
import utils.strUtils
import utils.listUtils
import utils.sysUtils
import shutil


# 显示文件夹结构 有正则过滤
def showDir(path_: str, reStrList_: list = None, depth_: int = 0):
    if depth_ == 0:
        print("root:[" + path_ + "]")
    for _item in os.listdir(path_):
        if reStrList_ is None or not (utils.strUtils.isStrInFilterList(reStrList_, _item)):
            print("|      " * depth_ + "+--" + _item)
            _newitem = path_ + '/' + _item
            if os.path.isdir(_newitem):
                showDir(_newitem, reStrList_, depth_ + 1)


# 显示文件夹结构
def showDir(path_: str, depth_: int = 0, prefix_: str = ""):
    if depth_ == 0:
        print(prefix_ + "root:[" + path_ + "]")
    for _item in os.listdir(path_):
        _newitem = path_ + os.sep + _item
        if os.path.isdir(_newitem):
            print(prefix_ + "|      " * depth_ + "+--" + _item)
            showDir(_newitem, depth_ + 1, prefix_)


# 显示文件结构
def showDirFile(path_: str, depth_: int = 0, prefix_: str = ""):
    if depth_ == 0:
        print(prefix_ + "root:[" + path_ + "]")
    _fileList = []
    for _item in os.listdir(path_):
        _newitem = path_ + os.sep + _item
        if os.path.isdir(_newitem):
            print(prefix_ + ("|" + " " * 6) * depth_ + "+--" + _item)
            showDirFile(_newitem, depth_ + 1, prefix_)
        else:
            _fileList.append(_item)

    for _file in _fileList:
        print(prefix_ + ("|" + " " * 6) * depth_ + "|--" + _file)


# 获取文件夹 仅仅 一层文件夹
def getFolderListJustOneDepth(path_: str):
    _folderList = []
    for _item in os.listdir(path_):
        _filePath = os.path.join(path_, _item)
        if os.path.isdir(_filePath):
            _folderList.append(_item)
    return _folderList


# 获取文件 仅仅 一层文件夹
def getFileListJustOneDepth(path_: str, fileFilter_: list):
    _fileList = []
    for _item in os.listdir(path_):
        _filePath = os.path.join(path_, _item)
        if not os.path.isdir(_filePath):
            if fileFilter_:  # 过滤的后缀列表
                _fileSuffix = os.path.splitext(_filePath)[1]  # 当前的文件，后缀名
                if _filePath and not _fileSuffix == "" and (_fileSuffix in fileFilter_):
                    _fileList.append(_item)
            else:  # 没有需要过滤的后缀列表，就全部记录下来
                _fileList.append(_item)
    return _fileList


# 保存文件之前先判断此文件是否存在，如果不存在，先创建父文件夹
def makeSureDirIsExists(path: str):
    dirs = path[0:path.rindex('/')]
    dirsExists = os.path.exists(dirs)
    if not dirsExists:
        os.makedirs(dirs)


def removeFileByFilter(folderPath_: str, fileFilter_: list):
    _filePathList = getFileListInFolder(folderPath_, fileFilter_)
    for _i in range(len(_filePathList)):
        utils.fileUtils.removeExistFile(_filePathList[_i], True)


# 获取某一类型的文件的大小总和
def getFileSizeInFolder(folderPath_: str, filters_: list):
    _filePathList = getFileListInFolder(folderPath_, filters_)
    _totalSize = 0
    for _i in range(len(_filePathList)):
        _totalSize = _totalSize + utils.fileUtils.getFileSize(_filePathList[_i])
    return _totalSize


# 在这个文件夹中，类型列表中的每一个类型大小各自为多少
def getFileSizeInFolderByTypes(folderPath_: str, types_: list):
    _totalSize = 0
    for _i in range(len(types_)):
        _fileType = types_[_i]
        _fileSizes = getFileSizeInFolder(folderPath_, [_fileType])
        _currentSize = _fileSizes / 1024 / 1024
        _totalSize = _totalSize + _currentSize
        print(_fileType + " : " + '%.2f' % _currentSize + " MB")
    print("all : " + '%.2f' % _totalSize + " MB")


# 将文件夹内指定文件类型进行大小排序显示
def getFileSizeInfoSortList(folderPath_: str, filters_: list):
    _filePathList = getFileListInFolder(folderPath_, filters_)
    _fileSizeInfoList = []
    for _i in range(len(_filePathList)):
        _fileInfo = {}
        _fileInfo["size"] = utils.fileUtils.getFileSize(_filePathList[_i])
        _fileInfo["filePath"] = _filePathList[_i]
        _fileSizeInfoList.append(_fileInfo)
    utils.listUtils.sortListOfDict(_fileSizeInfoList, "size", True)

    for _i in range(len(_fileSizeInfoList)):
        _filePath = _fileSizeInfoList[_i]["filePath"]
        _fileSize = _fileSizeInfoList[_i]["size"] / 1024
        print(str(round(_fileSize, 2)) + "KB : " + _filePath)

    return _fileSizeInfoList


# 在这个文件夹中，每一类文件占多少空间
def getFolderSizeInfo(folderPath_: str):
    getFileSizeInFolderByTypes(folderPath_, getSuffixsInFolder(folderPath_))


# 获取 文件夹内所有文件的后缀集合
def getSuffixsInFolder(filePath_: str):
    # 后缀名集合
    _suffixList = []
    # 文件夹内所有的文件
    _fileList = getFileListInFolder(filePath_)
    for _i in range(len(_fileList)):
        _filePath = _fileList[_i]
        _suffix = utils.fileUtils.getSuffix(_filePath)
        if not _suffix == "" and not (_suffix in _suffixList):
            _suffixList.append(_suffix)  # 记录后缀
    return _suffixList


# 遍历文件夹，按照后缀获取文件列表
def gci(filepath_: str, fileFilter_: list, fileList_: list = None):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath_)
    for fi in files:
        fi_d = os.path.join(filepath_, fi)
        if os.path.isdir(fi_d):
            gci(fi_d, fileFilter_, fileList_)
        else:
            _filePath = os.path.join(filepath_, fi_d)
            _fileSuffix = os.path.splitext(_filePath)[1]  # 当前的文件，后缀名
            if fileFilter_:  # 过滤的后缀列表
                if _filePath and not _fileSuffix == "" and (_fileSuffix in fileFilter_):
                    fileList_.append(_filePath)
            else:  # 没有需要过滤的后缀列表，就全部记录下来
                fileList_.append(_filePath)


# 将符合后缀类型的文件，构成 名称:路径 这样的键值对。
def getFilePathKeyValue(folder_: str, filters_: list):
    _filePathList = getFileListInFolder(folder_, filters_)
    _keyValueDict = {}
    # 文件列表 转换 键值对 <文件名:路径>
    for _i in range(len(_filePathList)):
        _value = _filePathList[_i]
        _key = os.path.basename(_value)
        if _key in _keyValueDict:
            raise Exception(
                _key + "已经存在 : \n" +
                "已有 : " + _keyValueDict[_key] + "\n" +
                "当前 : " + _value
            )
        else:
            _keyValueDict[_key] = _value
    return _keyValueDict


# 获取后缀名的文件列表
# fileList = folderUtils.getFilterFilesInPath(folderPath_,[".jpg"])
def getFilterFilesInPath(folderPath_: str, filters_: list):
    _allFilePaths = []
    for root, dirs, files in os.walk(folderPath_):
        if filters_:  # 有过滤信息，就按照这个过滤
            _realFilePaths = [os.path.join(root, _file) for _file in files if
                              utils.fileUtils.getSuffix(_file) in filters_]
        else:  # 没有过滤信息，就去全要
            _realFilePaths = [os.path.join(root, _file) for _file in files]
        _allFilePaths = _allFilePaths + _realFilePaths
    return _allFilePaths


# 文件夹 folderPath_ 下的 oldName_ 文件更名为 newName_
def renameFileInFolder(folderPath_, oldName_, newName_):
    os.rename(os.path.join(folderPath_, oldName_), os.path.join(folderPath_, newName_))


# 文件目录是否有子文件夹
def isFolderHasSubFolder(folderPath_):
    if os.path.isdir(folderPath_):
        _filePathsInDir = os.listdir(folderPath_)
        for _fileName in _filePathsInDir:
            _filePath = os.path.join(folderPath_, _fileName)
            if os.path.isdir(_filePath):
                return True
    else:
        print("WARNING : folderUtils -> isFolderHasSubFolder : 不是一个文件夹 : " + folderPath_ + " ")
    return False


# 获取文件列表
def getFileListInFolder(folder_: str, filters_: list = None):
    _filePathList = []
    # fix 最后一个字符为 /
    folder_ = utils.sysUtils.folderPathFixEnd(folder_)
    if filters_ and len(filters_) > 0:
        # 遍历后缀抒写方式，必须是 ".后缀" 才合理
        for _i in range(len(filters_)):
            if filters_[_i] == "" or not filters_[_i][0] == ".":
                raise Exception(
                    "当前后缀为 : \'" + filters_[_i] + "\' ，后缀抒写必须是 .后缀 的格式"
                )
                return None
    # 获取文件列表
    gci(
        folder_,
        filters_,
        _filePathList
    )
    return _filePathList


# 文件夹中查找字符串------------------------------------------------------------------------------------------------------------------------
# strList_ 要找的字符串的列表
# fileFilters_ 在什么类型的文件中找
# folder_ 目标文件夹
# needAll_ 结果集中的文件,是否必须包含全部 strList_ 的字符串.
def findStrInFolder(strList_: list, fileFilters_: list, folder_: str, needAll_: bool = False):
    _fileList = getFileListInFolder(folder_, fileFilters_)
    _resultList = []
    for _filePath in _fileList:  # 循环文件列表
        # 每一个File都重置成空
        _lineInfo = None
        for _str in strList_:  # 循环要匹配的字符串
            _lineStr = utils.fileUtils.fileHasString(_filePath, _str)
            if not _lineStr:  # 有匹配到的行
                if _lineInfo:
                    _lineInfo = _lineInfo
                else:
                    # 这个File里有才会成
                    _lineInfo = {}
                    _lineInfo["lineList"] = []
                    _lineInfo["filePath"] = _filePath
                _lineInfo["lineList"].append(_lineStr)

        if _lineInfo:  # 当前文件，是否有匹配消息
            if needAll_:  # 是否列表中的所有字符串都要满足
                _findCount = 0
                for _str in strList_:  # 传进来的每一个字符串,都满足
                    for _line in _lineInfo["lineList"]:
                        if _line.find(_str) >= 0:
                            _findCount += 1  # 找到当前的，就找下一个
                            break
                # 找到个数和要找的个一致，那么，这个文件就包含全部要找的内容
                if _findCount == len(strList_):
                    _resultList.append(_lineInfo)
            else:  # 不需要都满足，只要有匹配消息，就可以添加给返回值了
                _resultList.append(_lineInfo)
    return _resultList


# 备份文件夹，在当前文件夹所在的位置下，判断并创建副本
def folderBackUp(folderPath_):
    _folderParentPath = utils.sysUtils.getParentPath(folderPath_)  # 上层路径
    _backUpPath = os.path.join(_folderParentPath, utils.fileUtils.justName(folderPath_) + "_backUp")  # 搞一份备份
    if os.path.exists(_backUpPath):  # 有备份
        if not os.path.exists(folderPath_):  # 没有源，有可能删了。【代码执行错误的时候，会删除源，因为，源会变】
            shutil.copytree(_backUpPath, folderPath_)  # 将备份 同步给 源
            print("备份文件，拷贝回源路径")
        else:
            shutil.rmtree(folderPath_)  # 有源，这里的源，也是备份之后的，所以，可以用备份覆盖回去
            shutil.copytree(_backUpPath, folderPath_)
            utils.fileUtils.writeFileWithStr(folderPath_ + '/backup_created', 'backup end')  # 标记已经备份过了
            print("删除原路径，将备份还原回去")
        if not os.path.isfile(folderPath_ + '/backup_created'):  # 源里没有 创建备份的标示。
            shutil.rmtree(_backUpPath)  # 删除 原有备份
            shutil.copytree(folderPath_, _backUpPath)
            utils.fileUtils.writeFileWithStr(folderPath_ + '/backup_created', 'backup end')  # 标记已经备份过了
        else:
            print("已经创建过备份了")
    else:
        shutil.copytree(folderPath_, _backUpPath)  # 没备份文件 - 就备份一份
        utils.fileUtils.writeFileWithStr(folderPath_ + '/backup_created', 'backup end')  # 标记已经备份过了


# 文件夹中的每一个符合条件的文件，进行内容转换，重新写入另一个文件夹内
def convertFolderFiles(convertFunc_, srcFolderPath_: str, targetFolderPath_: str, filters_: list):
    _srcFile = utils.fileUtils.getPath(srcFolderPath_, "")
    _filePathList = getFileListInFolder(_srcFile, filters_)
    for _path in _filePathList:
        print(_path.split(srcFolderPath_).pop())
        _convertedStr = convertFunc_(_path)  # 路径指定文件内容转换并输出
        _targetFilePath = targetFolderPath_ + _path.split(srcFolderPath_).pop()  # 写入路径
        utils.fileUtils.writeFileWithStr(_targetFilePath, _convertedStr)


# 文件夹内的每一个符合条件的文件，执行方法
def doFunForeachFileInFolder(func_, srcFolderPath_: str, filters_: list):
    _csCodeFolder = utils.fileUtils.getPath(srcFolderPath_, "")
    _filePathList = getFileListInFolder(_csCodeFolder, filters_)
    for _path in _filePathList:
        print(_path)
        func_(_path)


if __name__ == "__main__":
    # 输出某个文件夹内文件种类构成以及大小分别是多少。
    _targetFolder = "/Volumes/Files/develop/loho/mini-game/miniclient/build/wechatgame/res/"
    getFolderSizeInfo(_targetFolder)

    # # 获取目标文件夹内，有哪些种类的文件
    # _targetFolder = "/Volumes/Files/develop/loho/mini-game/miniclient/build/wechatgame/res/"
    # _suffixList = getSuffixsInFolder(_targetFolder)
    # for _i in range(len(_suffixList)):
    #     print(str(_suffixList[_i]))
