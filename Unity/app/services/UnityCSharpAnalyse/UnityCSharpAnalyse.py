#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
import re


# 分析 C# 文件，修改其内容，为函数添加输出【最好配合Git，省得在单独备份文件】
class UnityCSharpAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        self.funcRegStr = r'^([=\.\[\] ,<>a-zA-Z0-9_\t]*)\s+([a-zA-Z0-9_]+)\s*\(\s*([^\)]*)\s*\)\s*\{'
        # self.folder = "/Volumes/18604037792/develop/ShunYuan/farmLua/Assets/Fabric/Editor/GUI/"
        self.folder = "/Volumes/18604037792/develop/ShunYuan/farmLua/Assets/Fabric/Editor/ThirdParty/"
        self.notFuncNameList = [
            "using", "catch", "lock",
            "if", "switch", "while",
            "for", "foreach"
        ]
        self.funcTypeList = [
            "public", "private", "protected"
        ]
        self.classTypeList = [
            "public", "protected", "internal", "private"  # protected internal
        ]
        self.curlyBracesUnCloseShortFileNameList = [

        ]

    def create(self):
        super(UnityCSharpAnalyse, self).create()

        self.getSubClassObject("RemoveComment")
        self.getSubClassObject("AdjustIfElse")
        self.getSubClassObject("AdjustClassFunc")
        self.getSubClassObject("AdjustDelegate")
        self.getSubClassObject("CurlyBraces")
        self.getSubClassObject("AnalyseStructure")
        self.getSubClassObject("AddStackFuncLog")
        self.getSubClassObject("DrawClassRelation")

        # 第一步。拷贝代码文件到临时目录，避免修改源文件
        # 过程生成文件的承载文件夹
        # _baseFolderPath = "/Volumes/18604037792/develop/ShunYuan/farmNew/"
        # # 工程内创建临时目录，盛放过程文件
        # _tempCopyFolder = 'CodeAnalyse/C#/Temp/'
        # # 拷贝出来，展示结构
        # fileCopyUtils.copyFilesInFolderTo([".cs"], _baseFolderPath + "Assets/", _baseFolderPath + _tempCopyFolder + 'Codes/', "include", True)
        # # 移除掉所有的UTF-8前缀
        # for _filePath in folderUtils.getFileListInFolder(_baseFolderPath + _tempCopyFolder + 'Codes/'):
        #     fileUtils.removeBomInUTF8(_filePath)
        # print("Show Dir -- ")
        # folderUtils.showDir(_baseFolderPath + _tempCopyFolder + 'Codes/')
        # print("Show Files -- ")
        # folderUtils.showDirFile(_baseFolderPath + _tempCopyFolder + 'Codes/')
        #
        # # 第二步，拷贝出的文件进行处理
        # self.removeComment.removeCSharpCommentInFolder(
        #     _baseFolderPath+_tempCopyFolder+'Codes/',
        #     _baseFolderPath+_tempCopyFolder+'Codes_removeComment/'
        # )
        # self.adjustClassFunc.adjustClassFuncVariableLineFolder(
        #     _baseFolderPath+_tempCopyFolder+'Codes_removeComment/',
        #     _baseFolderPath+_tempCopyFolder+'Codes_removeComment_adjustClassFunc/'
        # )
        #
        # # 第三步，对加工后的文件，进行一些校验 查找出大括号没有闭合的类
        # _curlyBracesNotCloseFileList = self.curlyBraces.cSharpCurlyBracesFileObject.checkCulyBracesFolder(
        #     _baseFolderPath+_tempCopyFolder+"Codes_removeComment_adjustClassFunc/"
        # )
        # if len(_curlyBracesNotCloseFileList) > 0:
        #     print("* 大括号没有闭合的代码 : ")
        #     for _curlyBracesNotCloseFile in _curlyBracesNotCloseFileList:
        #         print(_curlyBracesNotCloseFile)
        #
        # # 第四步，指定过滤文件，然后解析非过滤文件的结构
        # # self.curlyBracesUnCloseShortFileNameList = [
        # #     "Plugins/icsharpcode-SharpZipLib/src/Zip/Compression/Streams/DeflaterOutputStream.cs",
        # #     "Plugins/UnityPurchasing/script/IAPDemo.cs"
        # # ]
        # self.curlyBracesUnCloseShortFileNameList = []
        # _fileClassFuncDict = self.analyseStructure.analyseFileInfo(
        #     _baseFolderPath+_tempCopyFolder+"Codes_removeComment_adjustClassFunc/Editor/",
        #     self.curlyBracesUnCloseShortFileNameList
        # )
        #
        # self.drawClassRelation.drawClassRelation(
        #     _fileClassFuncDict,
        #     _baseFolderPath+"CodeAnalyse/ClassRelation/Editor/",
        # )
        #
        # self.drawClassRelation.drawClassRelationWithOutFolderStructure(
        #     _fileClassFuncDict,
        #     _baseFolderPath+"CodeAnalyse/ClassRelation/Editor/",
        #     True
        # )
        #
        # self.addStackFuncLog.addFuncInOutLogFolder(
        #     _baseFolderPath+_tempCopyFolder+"Codes_removeComment_adjustClassFunc/",
        #    _baseFolderPath+_tempCopyFolder+"Codes_removeComment_adjustClassFunc_funcStackLog/",
        #     _fileClassFuncDict
        # )

        # -----------------
        # 给某个文件夹 添加 Log输出
        # _baseFolderPath = "/Volumes/18604037792/develop/ShunYuan/farmNew/"
        # _baseCSharpFolderPath = _baseFolderPath+'Assets/LuaFramework'
        # _subFolderPath = '/ToLua/Source/Generate/'

        # _baseFolderPath = "/Volumes/18604037792/Unity/Self/SpineTest/"
        # _baseCSharpFolderPath = _baseFolderPath+'Assets/Spine/Runtime/'
        # _subFolderPath = ''

        _baseFolderPath = "/Volumes/Files/develop/GitHub/tolua/"
        _baseCSharpFolderPath = _baseFolderPath + 'Assets/'
        _subFolderPath = ''

        _targetFolder = _baseCSharpFolderPath + _subFolderPath
        self.removeComment.removeCSharpCommentInFolder(_targetFolder, _targetFolder)
        self.adjustClassFunc.adjustClassFuncVariableLineFolder(_targetFolder, _targetFolder)

        # # ToLua
        # _fileClassFuncDict = self.analyseStructure.analyseFileInfo(_targetFolder, [
        #     "Core/",
        #     "Editor/",
        #     # "Generate/DelegateFactory.cs",
        #     # "Generate/LuaBinder.cs",
        # ])
        # # Scripts
        # _fileClassFuncDict = self.analyseStructure.analyseFileInfo(_targetFolder, [
        #     "Utility/LitJson/",
        #     "Utility/Mono",
        # ])
        # # /ToLua/Core/
        # _fileClassFuncDict = self.analyseStructure.analyseFileInfo(_targetFolder, [
        # ])



        _fileClassFuncDict = self.analyseStructure.analyseFileInfo(_targetFolder, [
            "Source/Generate/DelegateFactory.cs",
            "Source/Generate/LuaBinder.cs",
            "ToLua/Editor/",
            "LogUtils.cs",
            "TestDelegate.cs",
            "TestEventListener.cs"
        ])

        self.addStackFuncLog.addFuncInOutLogFolder(_targetFolder, _targetFolder, _fileClassFuncDict)

        # print("正在移除注释")
        # self.removeComment.removeCSharpCommentInFolder(
        #     _baseFolderPath + "C#/",
        #     _baseFolderPath + "C#_removeComment/"
        # )
        #
        # print("正在调整抒写 -- if else")
        # self.adjustIfElse.adjustIfElseFolder(pass :
        #     _baseFolderPath + "C#_removeComment/",
        #     _baseFolderPath + "C#_removeComment_adjust_ifElse/"
        # )
        #
        # print("正在调整抒写 -- class func")
        # self.adjustClassFunc.adjustClassFuncVariableLineFolder(
        #     _baseFolderPath + "C#_removeComment_adjust_ifElse/",
        #     _baseFolderPath + "C#_removeComment_adjust_classFunc/"
        # )
        #
        # print("正在调整抒写 -- delegate")
        # self.adjustDelegate.adjustDelegateFolder(
        #     _baseFolderPath + "C#_removeComment_adjust_classFunc/",
        #     _baseFolderPath + "C#_removeComment_adjust_classFunc_delegate/"
        # )
        #
        # print("正在解析Func抒写LOG")
        # self.addStackFuncLog.addFuncInOutLogFolder(
        #     _baseFolderPath + "C#_removeComment_adjust_classFunc_delegate/LuaFramework/",
        #     _baseFolderPath + "C#_removeComment_adjust_classFunc_delegate_Log/LuaFramework/")

    def destory(self):
        super(UnityCSharpAnalyse, self).destory()
