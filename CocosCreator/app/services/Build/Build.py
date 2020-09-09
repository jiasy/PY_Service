#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import fileUtils
from utils import gitUtils
from utils import strUtils
from utils import ftpUtils
from utils import folderUtils
import json
from utils import sysUtils
from PIL import Image
import matplotlib.pyplot as plt
import functools
import os


class Build(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(Build, self).create()
        self.cocosCreatorAppPath = "/Applications/CocosCreator.app/Contents/MacOS/CocosCreator"
        self.buildMiniClient_WeChat()

    def destory(self):
        super(Build, self).destory()

    # 编译 loho 的 miniClient
    def buildMiniClient_WeChat(self):
        # 工程路径
        _projectFolderPath = sysUtils.folderPathFixEnd("/Volumes/Files/develop/loho/mini-game/miniclient/")
        _assetsFolderPath = sysUtils.folderPathFixEnd(_projectFolderPath + "assets")
        _appConfigJsonPath = _projectFolderPath + "assets/resources/configs/AppConfig.json"
        # 打包配置路径
        _miniClientJsonPath = fileUtils.getPath(self.resPath, "WeChatGameConfig.json")
        # 打包配置内容
        _miniClientJsonDict = fileUtils.dictFromJsonFile(_miniClientJsonPath)
        # 获取构建之后的目录
        _buildFolderPath = sysUtils.folderPathFixEnd(_miniClientJsonDict["buildPath"]) + "wechatgame"
        # 获取构建之后的res目录
        _resFolderPath = sysUtils.folderPathFixEnd(_buildFolderPath) + "res/"

        print("请确保所有内容都已经 push 到远程，这样才能创建正确的 TAG")
        # 获取Git链接
        _repo = gitUtils.getRepo(_projectFolderPath)
        # 获取当前满足版本格式的Tag中最大的tag号
        _tagStrList = [str(_tagName) for _tagName in _repo.tags if strUtils.isVersionStr(str(_tagName))]
        _tagStrList = sorted(_tagStrList, key=functools.cmp_to_key(strUtils.versionCompare), reverse=True)
        # 记录版本号
        _biggestTar = _tagStrList[0]
        print("当前最大 TAG : " + _biggestTar)
        # 增加最后一位的版本号
        _tagIntList = [int(_tarStr) for _tarStr in _biggestTar.split(".")]
        _tagIntList[-1] = _tagIntList[-1] + 1
        _currentTar = ".".join([str(_tarInt) for _tarInt in _tagIntList])
        # 填写到AppConfig.json中
        print("修改本地的AppConfig版本号为 : " + _currentTar)
        print("  *请注意，只是修改本地。从本地提交到微信小程序测试工具中。不通过Git Remote 推送")
        self.changeAppConfigJson(_appConfigJsonPath, _currentTar)
        # 在 Git 上创建 tag
        print("创建新 TAG : " + _currentTar)
        _repo.create_tag(_currentTar)

        # 构建工程
        _cmd = self.getBuildCmd(_projectFolderPath, _miniClientJsonPath)
        print("获取构建命令: \n" + _cmd)

        # 获取构建的LOG 并记录下来。
        _cmdLogFile = "\n".join(os.popen(_cmd).readlines())
        fileUtils.writeFileWithStr(_buildFolderPath + "buildLog.log", _cmdLogFile)

        # 修改game.json内的超时时间
        self.changeGameJson(_buildFolderPath)

        print("正在获取FTP链接")
        # 获取要上传的ftp的host
        _ftpHost = "ftp网址"
        _ftpUserName = "用户名"
        _ftpPassWord = "密码"
        _ftpSync = ftpUtils.getFTPSync(
            _ftpHost,
            _ftpUserName,
            _ftpPassWord,
            "路径/文件夹"
        )
        print("ftp链接获取成功，正在上传请稍后")

        # 指定目录为 res ，那么res中的内容对应同步
        ftpUtils.uploadFolder(_ftpSync, _resFolderPath)
        print("资源上传成功")

        return

        # # 显示FTP上的文件列表
        # self.showResOnFtp(_ftpSync)

        # # 显示 assets 中，最大的十张图
        # self.showTopTenPic(_assetsFolderPath)

    # 获取编译语句
    def getBuildCmd(self, projectFolder_: str, configJsonPath_: str):
        _cmd = self.cocosCreatorAppPath + \
               " --path " + projectFolder_ + \
               " --build \"configPath=" + configJsonPath_ + "\""
        return _cmd

    # 显示大小最大的10张图
    def showTopTenPic(self, folderPath_: str):
        _biggestList = folderUtils.getFileSizeInfoSortList(folderPath_, [".png", ".jpg"])
        plt.figure("biggest")  # 设置系列
        for _i in range(10):
            plt.imshow(Image.open(_biggestList[_i]["filePath"]))  # 显示到 plt
            plt.title(str(_i + 1) + " : " + str(round(_biggestList[_i]["size"] / 1024, 2)) + "KB")  # 设置标题
            plt.show()  # 显示到SciView

    # 修改 game.json 的超时时间设置
    def changeGameJson(self, buildFolderPath_: str):
        # game.json 的内容
        # {
        #     "deviceOrientation": "portrait",
        #     "networkTimeout": {
        #         "request": 5000,
        #         "connectSocket": 5000,
        #         "uploadFile": 5000,
        #         "downloadFile": 5000
        #     },
        #     "subpackages": []
        # }
        # 修改构建之后的 game.json 的内容
        # print('buildFolderPath_ = ' + str(buildFolderPath_))
        _gameJsonPath = sysUtils.folderPathFixEnd(buildFolderPath_) + "game.json"
        # print('_gameJsonPath = ' + str(_gameJsonPath))
        _gameJsonDict = fileUtils.dictFromJsonFile(_gameJsonPath)
        _gameJsonDict["networkTimeout"]["request"] = 60000
        _gameJsonDict["networkTimeout"]["connectSocket"] = 60000
        _gameJsonDict["networkTimeout"]["uploadFile"] = 60000
        _gameJsonDict["networkTimeout"]["downloadFile"] = 60000
        _jsonStr = str(json.dumps(_gameJsonDict, indent=4, sort_keys=False, ensure_ascii=False))
        fileUtils.writeFileWithStr(_gameJsonPath, _jsonStr)

    # 修改 appConfig.json
    def changeAppConfigJson(self, appConfigPath_: str, currentVer_: str):
        _appConfigDict = fileUtils.dictFromJsonFile(appConfigPath_)
        _appConfigDict["version"] = currentVer_
        _jsonStr = str(json.dumps(_appConfigDict, indent=4, sort_keys=False, ensure_ascii=False))
        fileUtils.writeFileWithStr(appConfigPath_, _jsonStr)
