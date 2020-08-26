#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import fileUtils
from utils import folderUtils
import json


# png meta
# {
#   "ver": "2.2.0",
#   "uuid": "8a52eb2f-380a-41b1-aa60-9bd65060d595",  # .png 的 uuid
#   "type": "sprite",
#   "wrapMode": "clamp",
#   "filterMode": "bilinear",
#   "premultiplyAlpha": false,
#   "subMetas": {
#     "chat_backbg": {
#       "ver": "1.0.3",
#       "uuid": "db886f00-0ada-4183-b6d9-f339a7d16dd4", # spriteFrame 的 uuid ，界面Sprite中引用的就是这个
#       "rawTextureUuid": "8a52eb2f-380a-41b1-aa60-9bd65060d595",
#       "trimType": "auto",
#       "trimThreshold": 1,
#       "rotated": false,
#       "offsetX": 0,
#       "offsetY": 0,
#       "trimX": 0,
#       "trimY": 0,
#       "width": 850,
#       "height": 531,
#       "rawWidth": 850,
#       "rawHeight": 531,
#       "borderTop": 0,
#       "borderBottom": 0,
#       "borderLeft": 0,
#       "borderRight": 0,
#       "subMetas": {}
#     }
#   }
# }


class MetaAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        self.projectFolder = "/Volumes/18604037792/develop/ShunYuan/wxGame"
        self.scriptFolder = self.projectFolder + "/assets/"
        self.prefabFolder = self.projectFolder + "/assets/"
        self.picFolder = self.projectFolder + "/assets/"
        # self.picFolder = self.projectFolder + "/assets/resources/textures/"
        self.soundFolder = self.projectFolder + "/assets/"

        # 获取所有图片
        self.picFiles = folderUtils.getFilterFilesInPath(self.picFolder, [".png", ".jpg"])

        # 获取plist文件
        self.plistFiles = folderUtils.getFilterFilesInPath(self.picFolder, [".plist"])
        self.plistPngs = [_plist.replace(".plist", ".png") for _plist in self.plistFiles]
        self.plistMeta = [_plist.replace(".plist", ".plist.meta") for _plist in self.plistFiles]

        # 获取非plist对应的图片
        self.normalPics = [_picFile for _picFile in self.picFiles if not _picFile in self.plistPngs]
        self.pngMetas = [_normalPicFile.replace(".png", ".png.meta") for _normalPicFile in self.normalPics if
                         _normalPicFile.endswith(".png")]
        self.jpgMetas = [_normalPicFile.replace(".jpg", ".jpg.meta") for _normalPicFile in self.normalPics if
                         _normalPicFile.endswith(".jpg")]

        # 图片的uuid集合，包含大图中碎图信息
        self.picMetaInfos = self.getPicSubMetaInfos(self.plistMeta) + self.getPicSubMetaInfos(
            self.pngMetas) + self.getPicSubMetaInfos(self.jpgMetas)

        # 获取prefab文件
        self.prefabFiles = folderUtils.getFilterFilesInPath(self.prefabFolder, [".prefab"])

    def create(self):
        super(MetaAnalyse, self).create()
        # # ------------------------------------------------------------------------------------------------------------
        # # 将mp3文件构成 名称:相对路径 的格式，然后解析成对应的代码格式
        # _soundProviderCode = self.getProviderCodeByFolder(
        #     self.soundFolder,  # 文件所在路径
        #     [".mp3"],  # 文件类型
        #     '    this.soundPathDict["{key}"] = "{path}";'  # 代码模板
        # )
        # print(_soundProviderCode)

        # ------------------------------------------------------------------------------------------------------------
        # 获取没使用的pic列表
        _unusePicList = self.getUnusePicList()
        if len(_unusePicList)>0:
            for _i in range(len(_unusePicList)):
                _item = _unusePicList[_i]
                print('_item = ' + str(_item))
        else:
            print("没有找到未使用的图片")

        # ------------------------------------------------------------------------------------------------------------
        # # prefab目录中替换UUID
        # self.replaceUuidInPrefabs(
        #     "7535bb24-248f-4c9c-9bf9-909351c12535",
        #     "9c0983da-e4aa-4775-848e-6a2e605fd0c0"
        # )

    def destory(self):
        super(MetaAnalyse, self).destory()

    # 遍历meta列表，获取所有Meta使用图片的uuid信息
    def getPicSubMetaInfos(self, fileMetas_: list):
        _metaInfos = []
        for _fileMeta in fileMetas_:
            _metaInfo = {}
            _fileMetaDict = fileUtils.dictFromJsonFile(_fileMeta)
            _metaInfo["filePath"] = _fileMeta.split(".meta")[0]
            _metaInfo["subUuids"] = []
            # 获取 文件中 subMetas ，这个就是当前图片中包含的单图信息[因为有些图是pack之后的大图]
            _subMeta = _fileMetaDict["subMetas"]
            for _key in _subMeta:
                # 循环 subMetas 得到其中包含的所有小图的uuid
                _metaInfo["subUuids"].append(_subMeta[_key]["uuid"])
            _metaInfos.append(_metaInfo)
        return _metaInfos

    # ------------------------------------------------------------------------------------------------------------
    # 遍历文件目录，获取文件名和文件路径的关系，将关系输出成字典结构
    # 遍历字典结构，将其输出成 provider.js 初始化键值对关系
    # 用来在游戏启动是预先加载所有资源
    def getProviderCodeByFolder(self, folder_: str, fileTypes_: list, codeTemplet_: str):
        _code = ""
        # 获取文件名和文件路径的字典
        _fileDict = folderUtils.getFilePathKeyValue(folder_, fileTypes_)
        for _key in _fileDict:
            _keyName = _key.split(".")[0]
            _pathWithOutSuffix = fileUtils.pathWithOutSuffix(_key, folder_)
            _relativePathWithOutSuffix = _pathWithOutSuffix.split(folder_)[1]
            _code = _code + codeTemplet_.format(key=_keyName, path=_relativePathWithOutSuffix) + "\n"
        return _code

    # ------------------------------------------------------------------------------------------------------------
    # 在prefab文件夹内，遍历每一个prefab文件。
    # 在prefab文件内容中，查找 uuid。
    # 如果查找到了，那么当前的meta对应的图片，其中的一张图就是有prefab在使用的。
    # 如果没有查找到，那么记录到没有查找到的列表中，就得到了没有使用过的图文件列表。
    def getUnusePicList(self):
        _unusePicList = []
        # 循环所有的uuid，看看那些prefab中没有使用
        for _i in range(len(self.picMetaInfos)):
            _metaInfos = self.picMetaInfos[_i]
            _uuids = _metaInfos["subUuids"]
            _inUsed = False
            for _idx in range(len(_uuids)):
                _uuid = _uuids[_idx]
                # 文件夹中查找字符串
                _fileInfoList = folderUtils.findStrInFolder(
                    [_uuid],
                    [".prefab"],
                    self.prefabFolder,
                    False
                )
                # 结果存在，就证明有地方引用
                if _fileInfoList and len(_fileInfoList) > 0:
                    _inUsed = True
                    break
            # 没有有prefab使用,记录它的文件路径
            if not _inUsed:
                _unusePicList.append(_metaInfos["filePath"])
        return _unusePicList

    # ------------------------------------------------------------------------------------------------------------
    # 遍历 prefab 将其中的一个uuid换成另外一个，从而实现换皮。
    def replaceUuidInPrefabs(self, sourceUuid_, targetUuid_):
        for _i in range(len(self.prefabFiles)):
            _prefabFilePath = self.prefabFiles[_i]
            print('_prefabFilePath = ' + str(_prefabFilePath))
            if fileUtils.fileHasString(_prefabFilePath, sourceUuid_):
                _prefabContent = fileUtils.readFromFile(_prefabFilePath).replace(sourceUuid_, targetUuid_)
                fileUtils.writeFileWithStr(_prefabFilePath, _prefabContent)
