# !/usr/bin/env python3

import re
from git import Repo  # 导入repo模块
import os
import json
import getopt
import sys
import functools
import ftplib
import stat
import shutil
from pathlib import Path, PureWindowsPath
import platform
import zipfile
import base64

fileUpdatedCount = 0
fileNeedToUpdate = 0


class FTPSync(object):
    def __init__(self, host_: str, username_: str, password_: str, ftpFolder_: str = None):
        self.ftpConnect = ftplib.FTP(host_, username_, password_)  # host, user, passwd
        self.ftpFolder = ""
        if ftpFolder_:
            # 去掉文件路径后面的 /
            if ftpFolder_[-1] == "/":
                ftpFolder_ = ftpFolder_[:-1]
            self.ftpFolder = ftpFolder_
            self.ftpConnect.cwd(self.ftpFolder)  # 远端FTP目录

    def get_dirs_files(self):
        u''' 得到当前目录和文件, 放入dir_res列表 '''
        dir_res = []
        self.ftpConnect.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
        return files, dirs

    # 遍历文件夹
    # ftpUtils.walk('.')
    def walk(self, next_dir, resultList_: list = None):
        # 文件列表
        _resultList = resultList_ if resultList_ else []
        # ftp 端切换到文件夹
        self.ftpConnect.cwd(next_dir)
        # ftp 端的文件夹
        ftp_curr_dir = self.ftpConnect.pwd()
        ftp_relative_curr_dir = ftp_curr_dir.split(self.ftpFolder)[1]
        # ftp 当前指向目录下的文件
        files, dirs = self.get_dirs_files()
        # ftp 端的文件相对路径
        for _file in files:
            _filePath = ftp_relative_curr_dir + "/" + _file
            _resultList.append(_filePath)
            print('_filePath = ' + str(_filePath))
        # 遍历文件夹
        for d in dirs:
            self.ftpConnect.cwd(ftp_curr_dir)  # 切换ftp的当前工作目录为d的父文件夹
            self.walk(d, _resultList)  # 在这个递归里面，本地和ftp的当前工作目录都会被更改
        # 返回结果集
        return _resultList

    # ftp.syncToLocal('.')
    def syncToLocal(self, next_dir):
        # ftp 端切换到文件夹
        self.ftpConnect.cwd(next_dir)
        # 本地创建相同的目录
        try:
            os.mkdir(next_dir)
        except OSError:
            pass
        os.chdir(next_dir)
        # ftp 端的文件夹
        ftp_curr_dir = self.ftpConnect.pwd()
        # 本机的文件夹
        local_curr_dir = os.getcwd()
        # ftp 当前指向目录下的文件
        files, dirs = self.get_dirs_files()
        # 遍历文件
        for f in files:
            print('download :', os.path.abspath(f))
            outf = open(f, 'wb')
            try:
                self.ftpConnect.retrbinary('RETR %s' % f, outf.write)
            finally:
                outf.close()
        # 遍历文件夹
        for d in dirs:
            os.chdir(local_curr_dir)  # 切换本地的当前工作目录为d的父文件夹
            self.ftpConnect.cwd(ftp_curr_dir)  # 切换ftp的当前工作目录为d的父文件夹
            self.syncToLocal(d)  # 在这个递归里面，本地和ftp的当前工作目录都会被更改


def uploadFolder(ftpSync_, localFolderPath_, ftpFolderPath_=None):
    print("%s" % (localFolderPath_))
    _ftpConnect = ftpSync_.ftpConnect
    _fileList = os.listdir(localFolderPath_)

    # 先记住之前在哪个工作目录中
    _lastFolder = os.path.abspath('.')
    # 然后切换到目标工作目录
    os.chdir(localFolderPath_)

    if ftpFolderPath_:
        _currentTargetFolderPath = _ftpConnect.pwd()
        try:
            _ftpConnect.mkd(ftpFolderPath_)
        except Exception:
            pass
        finally:
            _ftpConnect.cwd(os.path.join(_currentTargetFolderPath, ftpFolderPath_))

    for _fileName in _fileList:
        _currentTargetFolderPath = _ftpConnect.pwd()
        _currentLocal = localFolderPath_ + r'/{}'.format(_fileName)
        if os.path.isfile(_currentLocal):
            uploadFile(ftpSync_, localFolderPath_, _fileName)
        elif os.path.isdir(_currentLocal):
            _currentTargetFolderPath = _ftpConnect.pwd()
            try:
                _ftpConnect.mkd(_fileName)
            except:
                pass
            _ftpConnect.cwd("%s/%s" % (_currentTargetFolderPath, _fileName))
            uploadFolder(ftpSync_, _currentLocal)

        # 之前路径可能已经变更，需要再回复到之前的路径里
        _ftpConnect.cwd(_currentTargetFolderPath)

    os.chdir(_lastFolder)


def uploadFile(ftpSync_, localFolderPath_, fileName_, ftpFolderPath_=None, callback_=None):
    global fileUpdatedCount
    _ftpConnect = ftpSync_.ftpConnect
    # 记录当前 ftp 路径
    _currentFolder = _ftpConnect.pwd()

    if ftpFolderPath_:
        try:
            _ftpConnect.mkd(ftpFolderPath_)
        except:
            pass
        finally:
            _ftpConnect.cwd(os.path.join(_currentFolder, ftpFolderPath_))

    file = open(os.path.join(localFolderPath_, fileName_), 'rb')  # file to send
    _ftpConnect.storbinary('STOR %s' % fileName_, file, callback=callback_)  # send the file
    file.close()  # close file
    fileUpdatedCount = fileUpdatedCount + 1
    print(
        "    %s/%s %s / %s" % (
            str(fileUpdatedCount),
            str(fileNeedToUpdate),
            localFolderPath_,
            fileName_
        )
    )
    _ftpConnect.cwd(_currentFolder)


# 写文件
def writeFileWithStr(filePath_: str, str_: str):
    if not os.path.exists(os.path.dirname(filePath_)):
        os.makedirs(os.path.dirname(filePath_))
    try:
        _file = open(filePath_, 'w')
        try:
            _file.write(str_)
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)


# json文件直接读取成字典
def dictFromJsonFile(jsonPath_: str):
    return json.loads(readFromFile(jsonPath_))


def readFromFile(filePath_: str):
    _contentStr = None
    try:
        _file = open(filePath_, 'r')
        try:
            _contentStr = _file.read()
        finally:
            _file.close()
    except Exception as e:
        print(filePath_, e)
    return _contentStr


def versionCompare(v1: str = "1.1.1", v2: str = "1.2"):
    if not isVersionStr(v1) or not isVersionStr(v2):
        return None
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    v1_len = len(v1_list)
    v2_len = len(v2_list)
    if v1_len > v2_len:
        for i in range(v1_len - v2_len):
            v2_list.append("0")
    elif v2_len > v1_len:
        for i in range(v2_len - v1_len):
            v1_list.append("0")
    else:
        pass
    for i in range(len(v1_list)):
        if int(v1_list[i]) > int(v2_list[i]):
            # v1大
            return 1
        if int(v1_list[i]) < int(v2_list[i]):
            # v2大
            return -1
    # 相等
    return 0


# 检测当前名称是否是版本号 x.x.x
def isVersionStr(ver_: str):
    _verCheck = re.match("\d+(\.\d+){0,2}", ver_)
    if _verCheck is None or _verCheck.group() != ver_:
        return False
    else:
        return True


# 获取编译语句
def getBuildCmd(cocosCreatorAppPath_, projectFolder_: str, configJsonPath_: str):
    _cmd = cocosCreatorAppPath_ + \
           " --path " + projectFolder_ + \
           " --build \"configPath=" + configJsonPath_ + "\""
    return _cmd


# 修改 game.json 的超时时间设置
def changeGameJson(buildFolderPath_: str):
    _gameJsonPath = str(Path(buildFolderPath_ + "/wechatgame/game.json"))
    _gameJsonDict = dictFromJsonFile(_gameJsonPath)
    _gameJsonDict["networkTimeout"]["request"] = 60000
    _gameJsonDict["networkTimeout"]["connectSocket"] = 60000
    _gameJsonDict["networkTimeout"]["uploadFile"] = 60000
    _gameJsonDict["networkTimeout"]["downloadFile"] = 60000
    _jsonStr = str(json.dumps(_gameJsonDict, indent=4, sort_keys=False, ensure_ascii=False))
    writeFileWithStr(_gameJsonPath, _jsonStr)


# 修改 appConfig.json
def changeAppConfigJson(appConfigPath_: str, currentVer_: str, isTest_: bool):
    _appConfigDict = dictFromJsonFile(appConfigPath_)
    _appConfigDict["version"] = currentVer_
    if isTest_:
        # QA测试
        _appConfigDict["networkInfo"]["audit"] = "ws://ip:port"
        _appConfigDict["networkInfo"]["release"] = _appConfigDict["networkInfo"]["audit"]
    else:
        # 提审或者正式
        _appConfigDict["networkInfo"]["audit"] = "wss://网址"
        _appConfigDict["networkInfo"]["release"] = "wss://网址"
    _jsonStr = str(json.dumps(_appConfigDict, indent=4, sort_keys=False, ensure_ascii=False))
    writeFileWithStr(appConfigPath_, _jsonStr)


# 修改 WeChatGameConfig.json
# 修改其中的构建目录，指向当前build
def changeWeChatGameConfigJson(weChatGameConfigJsonPath_: str, buildPath_: str, isTest_: bool, ver_: str):
    _weChatGameConfigDict = dictFromJsonFile(weChatGameConfigJsonPath_)
    _weChatGameConfigDict["buildPath"] = buildPath_
    if isTest_:
        # QA测试
        _weChatGameConfigDict["wechatgame"][
            "REMOTE_SERVER_ROOT"] = "https://网址/QA_Test/" + ver_ + "/"
    else:
        # 提审或者正式
        _weChatGameConfigDict["wechatgame"][
            "REMOTE_SERVER_ROOT"] = "https://网址/wsg/" + ver_ + "/"
    _jsonStr = str(json.dumps(_weChatGameConfigDict, indent=4, sort_keys=False, ensure_ascii=False))
    writeFileWithStr(weChatGameConfigJsonPath_, _jsonStr)


def printList(list_: list, prefix_: str = ""):
    _length: int = len(list_)
    for _idx in range(_length):
        print(prefix_ + str(_idx) + ' : ' + str(str(list_[_idx])))


def os_is_mac():
    return platform.system() == "Darwin"


# 0 脚本文件在工程目录下
# 1 ssh登陆Git
# 2 确保当前目录都push到远程
# 3 可以填写 -v 作为版本指定，也可不填写，会默认在当前最大版本上加 0.0.1
# 4 WeChatGameConfig.json 填写构建参数，也就是构建的目标路径，使用的远程资源地址
# 5 assets/resources/configs/AppConfig.json 内为 wss 地址，当前版本号
# 6 流程如下
#      链接Git 获取tag信息，并创建一个新tag，确保它最大。
#      修改本地的appConfig
#      构建工程，并记录res下的文件个数
#      修改构建目录下的game.json，确保延时加载的时间为 6000 毫秒
#      将 res 目录上传至 ftp，
#      将 res 打包成 zip
#      成功后删除 本地 res
#      结束流程，之后就是手工的打开 微信开发者工具，手动上传即可。
# python3 CocosCreatorBuild.py -v 1.1.1
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "hv:")
    # 指定版本号
    _targetVersion = None
    # 获取版本号
    for _op, _value in opts:
        if _op == "-v":
            _targetVersion = _value
            if not isVersionStr(_targetVersion):
                print("ERROR 请输入正确的版本号格式 x.x.x")
                sys.exit(1)

    if _targetVersion:
        print("当前为 -- 提审 -- 版本号为 : " + _targetVersion)
    else:
        print("当前为 -- 测试 -- 包")

    # 注意文件目录都需要 / 结尾，否者会当做是文件。
    _cocosCreatorAppPath = "D:\\Softwares\\CocosCreator\\CocosCreator"
    if os_is_mac():
        _cocosCreatorAppPath = "/Applications/CocosCreator.app/Contents/MacOS/CocosCreator"

    # 工程路径
    _projectFolderPath = Path(os.getcwd() + "/")
    # 当前脚本文件名
    _pyFileName = Path(__file__).name
    #
    _pyFileRealPath = Path(str(_projectFolderPath) + "/" + _pyFileName)

    if not os.path.exists(str(_pyFileRealPath)):
        # 确保在自己所在的目录下执行脚本
        print("ERROR 确保在脚本所在的目录执行命令行 : " + str(_pyFileRealPath))
        sys.exit(1)

    # appConfig 路径
    _appConfigJsonPath = Path(str(_projectFolderPath) + "/assets/resources/configs/AppConfig.json")
    # 打包配置路径
    _weChatGameConfigJsonPath = Path(str(_projectFolderPath) + "/WeChatGameConfig.json")
    # 打包配置内容
    _miniClientJsonDict = dictFromJsonFile(str(_weChatGameConfigJsonPath))
    # 获取构建之后的目录
    _buildFolderPath = Path(str(_projectFolderPath) + "/build/")
    _buildBackFolderPath = Path(str(_projectFolderPath) + "/buildBack/")

    # 获取构建之后的res目录
    _resFolderPath = Path(str(_buildFolderPath) + "/wechatgame/res/")

    # 备份build  -------------------------------------------------------------------------------------------------
    # 判断当前的build 是否脚本发布生成的。如果是备份，如果不是删除，创建新的
    for _name in os.listdir(str(_buildFolderPath)):
        if _name.find("test_") == 0 or _name.find("ver_") == 0:
            shutil.copytree(str(_buildFolderPath), str(_buildBackFolderPath) + "/" + _name.split(".zip")[0])
            print("buildBack文件夹内创建 " + _name.split(".zip")[0] + " 备份")
            break;
    shutil.rmtree(str(_buildFolderPath))
    print("清空 原有 build")
    os.mkdir(str(_buildFolderPath))

    # 获取Git链接 -------------------------------------------------------------------------------------------------
    _repo = Repo.init(_projectFolderPath)

    # 获取当前满足版本格式的Tag中最大的tag号
    _tagStrList = [str(_tagName) for _tagName in _repo.tags if isVersionStr(str(_tagName))]
    _tagStrList = sorted(_tagStrList, key=functools.cmp_to_key(versionCompare), reverse=True)
    # 记录版本号
    _biggestTar = _tagStrList[0]
    print("当前最大 TAG : " + _biggestTar)

    # 只保留最大的10个tag号。
    for _i in range(9,len(_tagStrList)):
        _item = _tagStrList[_i]
        _repo.delete_tag(_item)

    if _targetVersion:
        if versionCompare(_targetVersion, _biggestTar) == -1:
            print("ERROR 输入的版本号 " + _targetVersion + " 不能小于 Git 上的最大版本号 " + _biggestTar)
            sys.exit(1)
        elif versionCompare(_targetVersion, _biggestTar) == 0:
            _currentTar = _targetVersion
            _repo.delete_tag(_currentTar)
        else:
            _currentTar = _targetVersion
    else:
        # 增加最后一位的版本号
        _tagIntList = [int(_tarStr) for _tarStr in _biggestTar.split(".")]
        _tagIntList[-1] = _tagIntList[-1] + 1
        _currentTar = ".".join([str(_tarInt) for _tarInt in _tagIntList])

    # 修改 weChatGameConfig.json ----------------------------------------------------------------------------------
    changeWeChatGameConfigJson(str(_weChatGameConfigJsonPath), str(_buildFolderPath), _targetVersion == None,
                               _currentTar)

    # 填写到AppConfig.json中 ---------------------------------------------------------------------------------------
    print("修改本地的AppConfig版本号为 : " + _currentTar)
    print("  *请注意，只是修改本地。从本地提交到微信小程序测试工具中。不通过Git Remote 推送")
    changeAppConfigJson(str(_appConfigJsonPath), _currentTar, _targetVersion == None)

    # 构建工程  -------------------------------------------------------------------------------------------------
    _cmd = getBuildCmd(_cocosCreatorAppPath, str(_projectFolderPath), str(_weChatGameConfigJsonPath))
    print("获取构建命令: \n" + _cmd)

    # 获取构建的LOG 并记录下来。
    _cmdLogFile = "\n".join(os.popen(_cmd).readlines())
    writeFileWithStr(str(Path(str(_buildFolderPath) + "/logs/CocosCreatorBuild.log")), _cmdLogFile)

    # 统计文件夹下文件个数  -----------------------------------------------------------------------------------------
    for _root, _dirs, _files in os.walk(str(_resFolderPath)):  # 遍历统计
        for _file in _files:
            fileNeedToUpdate = fileNeedToUpdate + 1

    # 修改game.json内的超时时间 -------------------------------------------------------------------------------------
    changeGameJson(str(_buildFolderPath))

    # 测试版本，需要开发者传ftp
    if not _targetVersion:
        # 获取要上传的ftp的host ---------------------------------------------------------------------------------
        _ftpHost = "ftp网址"
        _ftpUserName = "账户"
        _ftpPassWord = "密码"
        _ftpSync = FTPSync(
            _ftpHost,
            _ftpUserName,
            _ftpPassWord,
            "库名/文件夹/"
        )
        print("ftp链接获取成功，正在上传请稍后")
        # 创建版本号
        _ftpSync.ftpConnect.mkd(_currentTar)
        _ftpSync.ftpConnect.cwd(_currentTar)
        # 创建res文件夹
        _ftpSync.ftpConnect.mkd("res")
        _ftpSync.ftpConnect.cwd("res")
        # 指定目录为 res ，那么res中的内容对应同步
        uploadFolder(_ftpSync, str(_resFolderPath))
        print("资源上传成功")
    else:
        print('请将 ver_' + _currentTar + '.zip，发送给QA，由QA转交给运维，再上传FTP')

    # 测试和正式都需要记录res文件 ---------------------------------------------------------------------------------
    print("正在压缩 res ... ")
    _lastFolder = os.path.abspath('.')
    os.chdir(_buildFolderPath)
    if not _targetVersion:
        # 测试版自增获取版本号
        shutil.make_archive('test_' + _currentTar, 'zip', _resFolderPath)
    else:
        # 提审版，需要组合形成固定格式，区分自增的形式
        shutil.make_archive('ver_' + _currentTar, 'zip', _resFolderPath)
    os.chdir(_lastFolder)

    # 拥有全部权限，然后删除
    shutil.rmtree(_resFolderPath)
    print("删除本地 res : " + str(_resFolderPath))

    # 在 Git 上创建 tag ---------------------------------------------------------------------------------------
    print("创建新 TAG : " + _currentTar)
    if not _targetVersion:
        # 测试版自增获取版本号
        _repo.create_tag(_currentTar)
    else:
        # 提审版，需要组合形成固定格式，区分自增的形式
        _repo.create_tag("ver_" + _currentTar)

    # 微信开发者工具 ----------------------------------------------------------------------------------------------
    _buildType = None
    if _targetVersion:
        _buildType = "upload"
    else:
        _buildType = "debug"

    # 注意文件目录都需要 / 结尾，否者会当做是文件。
    _wxCliPath = "/Applications/wechatwebdevtools/"
    if os_is_mac():
        _wxCliPath = "/Applications/wechatwebdevtools.app/Contents/"

    # 注意文件目录都需要 / 结尾，否者会当做是文件。
    _shPath = str(_projectFolderPath) + "/wxWin.sh"
    if os_is_mac():
        _shPath = str(_projectFolderPath) + "/wxMac.sh"

    # 获取 sh 执行命令
    '''
    build_type=$1
    project_path=$2
    tool_path=$3
    version=$4
    version_desc=$5
    '''
    if _targetVersion:
        if os_is_mac():
            _cmd =\
            "sh " + _shPath + \
            " " + _buildType + \
            " " + str(_buildFolderPath) + "/wechatgame/" + \
            " " + str(Path(_wxCliPath)) + \
            " " + _currentTar + \
            " release" + _currentTar
        else:
            _cmd =\
            "sh " + str(PureWindowsPath(_shPath)) + \
            " " + _buildType + \
            " " + str(PureWindowsPath(str(_buildFolderPath))) + "/wechatgame/" + \
            " " + str(PureWindowsPath(str(Path(_wxCliPath)))) + \
            " " + _currentTar + \
            " release" + _currentTar
    else:
        if os_is_mac():
            _cmd = \
            "sh " + _shPath + \
            " " + _buildType + \
            " " + str(_buildFolderPath) + "/wechatgame/" + \
            " " + str(Path(_wxCliPath))
        else:
            _cmd = \
            "sh " + str(PureWindowsPath(_shPath)) + \
            " " + _buildType + \
            " " + str(PureWindowsPath(str(_buildFolderPath))) + "/wechatgame/" + \
            " " + str(PureWindowsPath(str(Path(_wxCliPath))))

    print("执行 微信开发者工具 命令")
    print(_cmd)


    if not os_is_mac():
        PureWindowsPath()



    # 执行命令，记录log
    _cmdLogFile = "\n".join(os.popen(_cmd).readlines())
    writeFileWithStr(str(Path(str(_buildFolderPath) + "/logs/wxUpload.log")), _cmdLogFile)

    # 还原二维码，并显示
    _imgDataStrPath = str(_buildFolderPath) + "/wechatgame/develop_code.txt";
    _imgDataStr = readFromFile(_imgDataStrPath).replace('data:image/jpeg;base64,', '')
    _imgData = base64.b64decode(_imgDataStr)
    _file = open(str(_buildFolderPath) + '/QrCode.jpg', 'wb')
    _file.write(_imgData)
    _file.close()
