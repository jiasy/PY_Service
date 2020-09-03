#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
import os


class SpineAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SpineAnalyse, self).create()

        _spineMainFolderPath = "/Volumes/18604037792/develop/ShunYuan/farmNew/SpineAssets/建筑Spine/"
        _outputFolderPath = _spineMainFolderPath + "output/"
        _spineList = folderUtils.getFolderListJustOneDepth(_spineMainFolderPath)
        for _i in range(len(_spineList)):
            _spineName = str(_spineList[_i])  # 文件夹名为Spine名
            _spineFolderPath = os.path.join(_spineMainFolderPath, _spineName)
            _imageFolderPath = os.path.join(_spineFolderPath, "images")  # 其中包含images文件夹
            _outFolderPath = os.path.join(_spineFolderPath, "out")  # 且包含一个输出文件夹
            if os.path.exists(_imageFolderPath) and os.path.exists(_outFolderPath):
                print("o - " + _spineName)
                # altas中的图片
                _pngList = self.pngListFromAltas(folderUtils.getFilterFilesInPath(_outFolderPath, [".txt"])[0])
                # 动画信息
                _jsonFilePath = folderUtils.getFilterFilesInPath(_outFolderPath, [".json"])[0]
                _jsonName = fileUtils.justName(_jsonFilePath)  # json名称
                _jsonDict = fileUtils.dictFromJsonFile(_jsonFilePath)

                # attachments 变更
                _slotAndPngRelationDict = _jsonDict["skins"][0]["attachments"]
                _tempDict = {}
                # 变更键名
                for _key in _slotAndPngRelationDict:
                    _tempDict[_key] = {}
                    for _pngKey in _slotAndPngRelationDict[_key]:
                        _pngInfoDict = _slotAndPngRelationDict[_key][_pngKey]
                        if not "type" in _pngInfoDict:
                            _tempDict[_key][_jsonName + "_" + _pngKey] = _pngInfoDict
                        else:
                            if _pngInfoDict["type"] == "mesh":
                                _tempDict[_key][_jsonName + "_" + _pngKey] = _pngInfoDict
                            else:
                                _tempDict[_key][_pngKey] = _pngInfoDict
                _jsonDict["skins"][0]["attachments"] = _tempDict

                # 更改后的json放置位置
                _jsonOutputPath = _outputFolderPath + _jsonName + ".json"
                fileUtils.dictToJsonFile(_jsonOutputPath, _jsonDict)

                # 图片字典
                _pngFolderPath = os.path.join(_outputFolderPath, _jsonName) + "/"
                fileCopyUtils.copyFilesInFolderTo(
                    [".png"],
                    _imageFolderPath,
                    _pngFolderPath,
                    "include",
                    True
                )
                _pngPathList = folderUtils.getFilterFilesInPath(_pngFolderPath, [".png"])
                for _j in range(len(_pngPathList)):
                    _pngName = fileUtils.justName(_pngPathList[_j])  # png名称
                    os.rename(_pngPathList[_j], _pngFolderPath + _jsonName + "_" + _pngName + ".png")
            else:
                print("x - " + _spineName)

    def pngListFromAltas(self, altasPath_: str):
        _atlasLines = fileUtils.linesFromFile(altasPath_)
        _lastLine = None
        _pngList = []
        for _i in range(len(_atlasLines)):
            _atlasLine = _atlasLines[_i]
            # 当前以空格起始
            if _atlasLine.startswith(" "):
                # 上一行存在
                if _lastLine:
                    # 上一行是图片
                    _pngList.append(_lastLine)
                    # 上一行清空
                    _lastLine = None
                else:
                    # 上一行不存在，上一行不是图片，当前行空格起始也不记录
                    _lastLine = None
            else:
                # 不是空白开始，记录当前行
                _lastLine = _atlasLine
        return _pngList

    def destory(self):
        super(SpineAnalyse, self).destory()
