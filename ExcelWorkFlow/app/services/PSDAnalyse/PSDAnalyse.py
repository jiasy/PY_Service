#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
from psd_tools import PSDImage
from psd_tools.constants import ColorMode
import io
from PIL import Image
import json


# 分析 PSD 文件结构，生成json文件。在Unity端解析结构生成UGUI
# https://psd-tools.readthedocs.io/en/latest/reference/psd_tools.html#
class PSDAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(PSDAnalyse, self).create()
        self.psdFolderPath = "/Volumes/18604037792/develop/ShunYuan/farmLua_analyse/PSD/"
        self.targetFolderPath = "/Volumes/Files/develop/selfDevelop/Unity/Flash2Unity2018/Assets/PSD/Resources/psd/"

        self.analysePsdFile("Balloon")

    def destory(self):
        super(PSDAnalyse, self).destory()

    def analysePsdFile(self, uiName_: str):
        _psdName = uiName_
        _psd = PSDImage.open(
            self.psdFolderPath + _psdName + ".psd"
        )

        if _psd.color_mode == ColorMode.RGB:
            print("psd color mode : RGB")

        print('_psd.channels = ' + str(_psd.channels))

        _psdDict = self.psdToJson(
            _psd,
            self.targetFolderPath,
            _psdName
        )

        _unityDict = {}
        _unityDict["name"] = _psdName
        _unityDict["type"] = "Root"
        _unityDict["bbox"] = {}
        _unityDict["bbox"]["left"] = _psdDict["bbox"]["left"]
        _unityDict["bbox"]["top"] = _psdDict["bbox"]["top"]
        _unityDict["bbox"]["right"] = _psdDict["bbox"]["right"]
        _unityDict["bbox"]["bottom"] = _psdDict["bbox"]["bottom"]
        self.convertToUnityUIJson(_psdDict, _unityDict)

        fileUtils.writeFileWithStr(
            self.targetFolderPath + "jsons/" + _psdName + ".json",
            str(json.dumps(_unityDict, indent=4, sort_keys=False, ensure_ascii=False))
        )

    def convertLayerName(self, layerName_: str):
        _layerName = layerName_
        if _layerName.find(' ') > 0 or _layerName.find('"') > 0 or _layerName.find('\'') > 0 or _layerName.find(
                '.') > 0 or _layerName.find('/') > 0:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "层名错误 : " + _layerName)
        return _layerName

    def convertToUnityUIJson(self, layerDict_: dict, unityGameObject_: dict):
        if not layerDict_["isVisible"]:
            return

        if not "layerList" in layerDict_:
            self.raiseError(
                pyUtils.getCurrentRunningFunctionName(),
                "不是层 : " + layerDict_["name"] + " - " + layerDict_["realName"] + " - " + str(layerDict_["isVisible"])
            )
        _currentIdx = 0

        unityGameObject_["children"] = []
        _layerDictList = layerDict_["layerList"]
        if _layerDictList:
            for _layerDict in _layerDictList:
                if not _layerDict["isVisible"]:
                    continue

                _unityLayerGameObject = {}
                _unityLayerGameObject["name"] = _layerDict["name"]
                _unityLayerGameObject["realName"] = _layerDict["realName"]
                _unityLayerGameObject["x"] = _layerDict["offsetX"]
                _unityLayerGameObject["y"] = _layerDict["offsetY"]
                _unityLayerGameObject["opacity"] = _layerDict["opacity"]
                _unityLayerGameObject["bbox"] = {}
                _unityLayerGameObject["bbox"]["left"] = _layerDict["bbox"]["left"]
                _unityLayerGameObject["bbox"]["top"] = _layerDict["bbox"]["top"]
                _unityLayerGameObject["bbox"]["right"] = _layerDict["bbox"]["right"]
                _unityLayerGameObject["bbox"]["bottom"] = _layerDict["bbox"]["bottom"]

                # 不同类型
                if str(_layerDict["name"]).startswith("pre_"):
                    _unityLayerGameObject["type"] = "prefab"
                    _subUIName = str(_layerDict["name"]).split("_")[1]  # 切出子ui名称
                    self.analysePsdFile(_subUIName)
                elif str(_layerDict["name"]).startswith("pic_"):
                    _unityLayerGameObject["type"] = "sprite"
                elif str(_layerDict["name"]).startswith("txt_"):
                    _unityLayerGameObject["type"] = "text"
                    _unityLayerGameObject["text"] = _layerDict["text"]
                    _unityLayerGameObject["fontSize"] = _layerDict["fontSize"]
                else:
                    _unityLayerGameObject["type"] = "gameObject"
                    self.convertToUnityUIJson(_layerDict, _unityLayerGameObject)

                # 获取层级
                _unityLayerGameObject["index"] = _currentIdx
                _currentIdx += 1
                # 记录节点
                unityGameObject_["children"].append(_unityLayerGameObject)

    def copyList(self, list_: list):
        _newList = []
        for _element in list_:
            _newList.append(_element)
        return _newList

    def layerPathsToName(self, paths_: list):
        _realName = ""
        _count = 0
        for _layerName in paths_:
            _layerName = self.convertLayerName(_layerName)
            if _count == 0:
                _realName = _layerName
            else:
                _realName = _realName + "&" + _layerName
            _count = _count + 1
        return _realName

    def psdToJson(self, psd_: PSDImage, targetFolderPath_: str, psdName_: str):
        _psdDict = {}
        _psdDict["name"] = psdName_
        _psdDict["realName"] = _psdDict["name"]
        _psdDict["paths"] = [_psdDict["name"]]
        _psdDict["isVisible"] = True
        _psdDict["opacity"] = 255

        _psdDict["viewbox"] = {}
        _psdDict["viewbox"]["left"] = psd_.viewbox[0]
        _psdDict["viewbox"]["top"] = psd_.viewbox[1]
        _psdDict["viewbox"]["right"] = psd_.viewbox[2]
        _psdDict["viewbox"]["bottom"] = psd_.viewbox[3]

        _psdDict["bbox"] = {}
        _psdDict["bbox"]["left"] = psd_.bbox[0]
        _psdDict["bbox"]["top"] = psd_.bbox[1]
        _psdDict["bbox"]["right"] = psd_.bbox[2]
        _psdDict["bbox"]["bottom"] = psd_.bbox[3]

        _psdDict["layerList"] = []
        _layerPathAndImageDict = {}
        for _layer in psd_:
            self.layerToJson(_layer, _psdDict, _layerPathAndImageDict, False)

        # 图片保存出来写入路径
        for _layerPathKey in _layerPathAndImageDict:
            _psdImage: PSDImage = _layerPathAndImageDict[_layerPathKey]
            _psdImage.save(targetFolderPath_ + "pngs/" + _layerPathKey + '.png')

        return _psdDict

    def layerToJson(self, layer_, parentLayerDict_: dict, layerPathAndImageDict_: dict, isClipLayer_=False):
        _layerDict = {}
        _layerDict["name"] = layer_.name
        _layerDict["paths"] = self.copyList(parentLayerDict_["paths"])
        _layerDict["paths"].append(_layerDict["name"])
        _layerDict["realName"] = self.layerPathsToName(_layerDict["paths"])
        _layerDict["blendMode"] = str(layer_.blend_mode).split("BlendMode.")[1]
        _layerDict["isVisible"] = layer_.is_visible()
        _layerDict["opacity"] = layer_.opacity  # 【0-255】
        _layerDict["bbox"] = {}
        _layerDict["bbox"]["left"] = layer_.bbox[0]
        _layerDict["bbox"]["top"] = layer_.bbox[1]
        _layerDict["bbox"]["right"] = layer_.bbox[2]
        _layerDict["bbox"]["bottom"] = layer_.bbox[3]
        _layerDict["hasMask"] = layer_.has_mask()
        _layerDict["hasOrigination"] = layer_.has_origination()
        _layerDict["hasStroke"] = layer_.has_stroke()

        _layerDict["clipLayerList"] = []
        for _clipLayer in layer_.clip_layers:
            self.layerToJson(_clipLayer, _layerDict, layerPathAndImageDict_, True)

        if not len(_layerDict["clipLayerList"]) > 0:
            del _layerDict["clipLayerList"]

        _layerDict["effects"] = []
        if layer_.has_effects():
            for _effect in layer_.effects:
                _effectDict = {}
                _effectDict["type"] = str(_effect)
                _effectDict["enabled"] = _effect.enabled
                _layerDict["effects"].append(_effectDict)
        if not len(_layerDict["effects"]) > 0:
            del _layerDict["effects"]

        _layerDict["offsetX"] = layer_.offset[0]
        _layerDict["offsetY"] = layer_.offset[1]

        if layer_.is_group():
            _layerDict["layerList"] = []
            for _childLayer in layer_:
                self.layerToJson(_childLayer, _layerDict, layerPathAndImageDict_, False)
            if not len(_layerDict["layerList"]) > 0:
                del _layerDict["layerList"]
        else:
            _layerDict["kind"] = layer_.kind
            if layer_.kind == "type":
                _layerDict["text"] = layer_.text
                _layerDict["fontSize"] = layer_.height + 2

        # 实际的图片资源
        if _layerDict["name"].startswith("pic_") or \
                _layerDict["name"].startswith("pre_") or \
                _layerDict["name"].startswith("txt_"):
            layerPathAndImageDict_[_layerDict["realName"]] = layer_.composite()

        if isClipLayer_:
            parentLayerDict_["clipLayerList"].append(_layerDict)
        else:
            parentLayerDict_["layerList"].append(_layerDict)
