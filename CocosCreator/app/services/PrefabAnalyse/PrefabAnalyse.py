#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *

# 分析界面和组件名称关系，按钮是否按照规范绑定
class PrefabAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        self._prefabFolder = "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/"
        self.typeList = []
        self.ccTypeList = [
            "cc.Prefab",
            "cc.Node",
            "cc.Sprite",
            "cc.PrefabInfo",
            "cc.Label",
            "cc.Button",
            "cc.Widget",
            "cc.LabelOutline",
            "cc.BoxCollider",
            "cc.Mask",
            "cc.ScrollView",
            "cc.BlockInputEvents",
            "cc.ClickEvent",
            "cc.Scrollbar",
            "cc.Layout",
            "cc.ProgressBar",
            "cc.EditBox",
            "cc.PolygonCollider",
            "cc.RichText"
        ]
        # 组件名 - 加密字符串 ------------------------------------
        # 组件名称和加密字符串对应关系字典
        self.componentClassEncryptDict = {}
        # 反过来的对应关系
        self.componentEncryptClassDict = {}

        # prefab 的 component 关系 -----------------------------
        self.prefabComponentDict = {}

    def create(self):
        super(PrefabAnalyse, self).create()

        # 分析 prefab 文件夹
        self.analysePrefabFolder()

        print("组件名 和 加密名 关系 --------------------------------------")
        for _className, _encryptStr in self.componentClassEncryptDict.items():
            print(_className + " : " + _encryptStr)

        print("未知类型 -------------------------------------------------")
        for _type in self.typeList:
            if not (_type in self.ccTypeList):  # 不是预制的组件
                if not (_type in self.componentEncryptClassDict):  # 不是已知 JS Component 挂载
                    print(_type)

        print("分析 prefab 文件 和 component 之间的关系---------------------")
        self.analysePrefabComponentRelationShip()
        for _key, _componentList in self.prefabComponentDict.items():
            print(_key + " : " + _componentList[0])

        print("分析 prefab 文件的结构 -------------------------------------")
        _pathList = self.analysePrefabFolderStructure()
        print("        自定义组件 ----------------------------------------")
        for _path in _pathList:
            if not _path.startswith("cc_"):
                print(_path)
        print("        官方组件 ------------------------------------------")
        for _path in _pathList:
            if _path.startswith("cc_"):
                _path = "cc." + _path.split("cc_")[1]
                print(_path)

        print("分析 prefab 中的按钮 --------------------------------------")
        self.analysePrefabFolderBtn()

    def destory(self):
        super(PrefabAnalyse, self).destory()

    # 解析 Prefab 上挂载 的 Component
    def analysePrefabFolder(self):
        _filePathDict = folderUtils.getFilePathKeyValue(self._prefabFolder, [".prefab"])
        for _, _filePath in _filePathDict.items():
            self.analysePrefab(_filePath)

    def analysePrefab(self, prefabPath_: str):
        _prefabList = fileUtils.dictFromJsonFile(prefabPath_)
        if isinstance(_prefabList, list):
            for _i in range(len(_prefabList)):
                _elementDict = _prefabList[_i]
                _elementType = _elementDict['__type__']
                if not (_elementType in self.typeList):
                    self.typeList.append(_elementType)
                    # 是有类名的Component
                    if "className" in _elementDict:
                        _className = _elementDict["className"]
                        if not (_className in self.componentClassEncryptDict):
                            self.componentClassEncryptDict[_className] = _elementType
                            self.componentEncryptClassDict[_elementType] = _className
        else:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), " 不是数组 : " + prefabPath_)

    # 解析 文件夹 Prefab 结构
    def analysePrefabFolderStructure(self):
        _prefabPathDict = folderUtils.getFilePathKeyValue(self._prefabFolder, [".prefab"])

        _pathList = []
        for _, _prefabPath in _prefabPathDict.items():
            self.analysePrefabStructure(_prefabPath, _pathList)

        # 所有的字段类型
        _pathList.sort()
        return _pathList

    # 解析 单一 prefab 结构
    def analysePrefabStructure(self, prefabPath_: str, pathList_: list):
        _prefabList = fileUtils.dictFromJsonFile(prefabPath_)
        for _i in range(len(_prefabList)):
            # prefab 的 每一个 元素
            _elementDict = _prefabList[_i]
            _type = _elementDict["__type__"]
            if _type.find("cc.") == 0:
                _type = "cc_" + _type.split(".").pop()
            else:
                if _type in self.componentEncryptClassDict:
                    _type = self.componentEncryptClassDict[_type]
            _changeList = self.sm.dc.sv(_type, _elementDict)
            # 过滤掉相同的变更路径
            for _changeIdx in range(len(_changeList)):
                _changePath = str(_changeList[_changeIdx])
                if not _changePath in pathList_:
                    pathList_.append(_changePath)

    # 解析 文件夹 Prefab 结构
    def analysePrefabFolderBtn(self):
        _prefabPathDict = folderUtils.getFilePathKeyValue(self._prefabFolder, [".prefab"])
        for _, _prefabPath in _prefabPathDict.items():
            self.analysePrefabBtn(_prefabPath)

    # 解析 单一 prefab 结构
    def analysePrefabBtn(self, prefabPath_: str):
        _prefabList = fileUtils.dictFromJsonFile(prefabPath_)
        print(prefabPath_.split(self._prefabFolder).pop() + " :")
        for _i in range(len(_prefabList)):
            # prefab 的 每一个 元素
            _elementDict = _prefabList[_i]
            _type = _elementDict["__type__"]
            # 节点是万物起源
            if _type == "cc.Node":
                _nodeName = _elementDict["_name"]
                _components = _elementDict["_components"]
                for _component in _components:
                    _componentId = _component["__id__"]
                    _componentDict = _prefabList[_componentId]
                    _componentType = _componentDict["__type__"]
                    # 包含按钮组件
                    if _componentType == "cc.Button":
                        _clickEvents = _componentDict["clickEvents"]
                        if len(_clickEvents) > 1 or len(_clickEvents) == 0:
                            print("    " + _nodeName + " 按钮组件 事件 触发 长度 为 " + str(len(_clickEvents)))
                        else:
                            if _clickEvents[0] is None:
                                print("    " + _nodeName + " 事件 是 空对象")
                            else:
                                print("    " + _nodeName + " 按钮组件 属性")
                                _clickEventId = _clickEvents[0]["__id__"]
                                _clickEvent = _prefabList[_clickEventId]
                                _clickEventComponentId = str(_clickEvent["_componentId"])
                                _componentName = ""
                                if _clickEventComponentId == "":
                                    _componentName = _clickEvent["component"]
                                else:
                                    if _clickEventComponentId in self.componentEncryptClassDict:
                                        _componentName = self.componentEncryptClassDict[
                                            _clickEventComponentId]
                                # if _componentName == "":
                                #     self.raiseError(pyUtils.getCurrentRunningFunctionName(), " 无组件名")
                                print("        " + '_componentName = ' + _componentName)

                                _customEventData = str(_clickEvent["customEventData"])
                                if not _customEventData == "":
                                    print("        " + 'customEventData = ' + _customEventData)

                                _hander = str(_clickEvent["handler"])
                                if not _hander == "":
                                    print("        " + '_hander = ' + _hander)

                                _clickEventTrargetId = str(_clickEvent["target"]["__id__"])
                                if not _clickEventTrargetId == "1":
                                    print("        " + 'target.__id__ = ' + _clickEventTrargetId)

    def analysePrefabComponentRelationShip(self):
        _prefabPathDict = folderUtils.getFilePathKeyValue(self._prefabFolder, [".prefab"])
        for _, _prefabPath in _prefabPathDict.items():
            _prefabFileName = fileUtils.justName(_prefabPath)
            # prefab 文件 对应 Component 的 列表
            self.prefabComponentDict[_prefabFileName] = []
            # prefab 的 列表
            _prefabList = fileUtils.dictFromJsonFile(_prefabPath)
            # prefab 内容
            for _i in range(len(_prefabList)):
                # prefab 的 每一个 元素
                _elementDict = _prefabList[_i]
                # 每一个 元素 的 类型
                _elementType = _elementDict['__type__']
                # 组件 和 加密字符串 的 对应字典。
                if _elementType in self.componentEncryptClassDict.keys():
                    _componentJSName = self.componentEncryptClassDict[_elementType]  # 转换成 js 脚本名
                    self.prefabComponentDict[_prefabFileName].append(_componentJSName)  # 获取 Prefab 上的 js Component 脚本

        _keyList = []
        for _key, _list in self.prefabComponentDict.items():
            if len(_list) == 0:
                _keyList.append(_key)

        for _key in _keyList:
            del self.prefabComponentDict[_key]

        for _key, _list in self.prefabComponentDict.items():
            if _key != _list[0]:
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                " 界面名 和 component 名称 不一致 " + _key + " : " + _list[0])
