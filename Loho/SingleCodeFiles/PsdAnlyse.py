# !/usr/bin/env python3
import os
from psd_tools import PSDImage
import json


# 写文件
def writeFileWithStr(filePath_, str_):
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


class PSDAnalyse(object):
    def __init__(self, psdFolderPath_: str, targetFolderPath_: str):
        self.psdFolderPath = psdFolderPath_
        self.targetFolderPath = targetFolderPath_

    def analysePsdFile(self, uiName_: str):
        _psdName = uiName_
        _psd = PSDImage.open(
            self.psdFolderPath + _psdName + ".psd"
        )

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

        writeFileWithStr(
            self.targetFolderPath + "jsons/" + _psdName + ".json",
            str(json.dumps(_unityDict, indent=4, sort_keys=False, ensure_ascii=False))
        )

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

        # 实际的图片资源
        if _layerDict["name"].startswith("pic_") or \
                _layerDict["name"].startswith("pre_") or \
                _layerDict["name"].startswith("txt_"):
            layerPathAndImageDict_[_layerDict["realName"]] = layer_.composite()

        if isClipLayer_:
            parentLayerDict_["clipLayerList"].append(_layerDict)
        else:
            parentLayerDict_["layerList"].append(_layerDict)

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

    def convertLayerName(self, layerName_: str):
        _layerName = layerName_
        if _layerName.find(' ') > 0 or _layerName.find('"') > 0 or _layerName.find('\'') > 0 or _layerName.find(
                '.') > 0 or _layerName.find('/') > 0:
            print('ERROR : ' + str("层名错误 : " + _layerName))
        return _layerName

    def convertToUnityUIJson(self, layerDict_: dict, unityGameObject_: dict):
        if not layerDict_["isVisible"]:
            return

        if not "layerList" in layerDict_:
            print('ERROR : ' + str(
                "不是层 : " + layerDict_["name"] + " - " + layerDict_["realName"] + " - " + str(layerDict_["isVisible"])
            ))
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
                else:
                    _unityLayerGameObject["type"] = "gameObject"
                    self.convertToUnityUIJson(_layerDict, _unityLayerGameObject)

                # 获取层级
                _unityLayerGameObject["index"] = _currentIdx
                _currentIdx += 1
                # 记录节点
                unityGameObject_["children"].append(_unityLayerGameObject)


if __name__ == "__main__":
    _psdAnalyse = PSDAnalyse(
        "/Volumes/18604037792/develop/ShunYuan/farmLua_analyse/PSD/",
        "/Volumes/Files/develop/selfDevelop/Unity/Flash2Unity2018/Assets/PSD/Resources/psd/"
    )
    _psdAnalyse.analysePsdFile("Balloon")
