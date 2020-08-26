#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *


# 分析 lua 文件，修改其内容，为函数添加输出【最好配合Git，省得在单独备份文件】
class UnityLuaAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(UnityLuaAnalyse, self).create()

        self.getSubClassObject("LuaRemoveComment")
        self.getSubClassObject("LuaAdjustClassFunc")
        self.getSubClassObject("LuaFuncStackLog")

        # 过程生成文件的承载文件夹
        _baseFolderPath = "/Volumes/18604037792/develop/ShunYuan/farmNew/Assets/LuaFramework/Lua/"

        # 移除注释
        self.luaRemoveComment.luaRemoveCommentInFolder(
            _baseFolderPath,
            _baseFolderPath
        )

        self.luaAdjustClassFunc.checkLuaStyle(
            _baseFolderPath
        )

        self.luaFuncStackLog.addFuncStackLogFolder(
            _baseFolderPath,
            _baseFolderPath
        )


        # # 拷贝出来，展示结构
        # fileCopyUtils.copyFilesInFolderTo([".lua"], _baseFolderPath, "/Volumes/18604037792/develop/ShunYuan/farmNew/CodeAnalyse/Lua/Temp/Codes/", "include", True)
        #
        # # 移除掉所有的UTF-8前缀
        # for _filePath in folderUtils.getFileListInFolder("/Volumes/18604037792/develop/ShunYuan/farmNew/CodeAnalyse/Lua/Temp/Codes/"):
        #     fileUtils.removeBomInUTF8(_filePath)
        #
        # print("Show Dir -- ")
        # folderUtils.showDir("/Volumes/18604037792/develop/ShunYuan/farmNew/CodeAnalyse/Lua/Temp/Codes/")
        # print("Show Files -- ")
        # folderUtils.showDirFile("/Volumes/18604037792/develop/ShunYuan/farmNew/CodeAnalyse/Lua/Temp/Codes/")

    def destory(self):
        super(UnityLuaAnalyse, self).destory()
