#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import pyUtils
from utils import fileUtils
import subprocess


# 将文件和Proto的关系用dot图表示
class CodeAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        self.protoResAndReq = []
        self.protoReq = []
        self.protoRes = []
        self.protoSyn = []
        self.protoOther = []

        # 组件列表
        self.componentNameList = ["ArchitectureUnLock", "BaseGoodChange", "CropIcon", "CropItem", "InformationNode",
                                  "PlantCrop", "SaleGood", "BBS", "BindPublic", "BuyGood", "CashTask", "ConnectNet",
                                  "Crop", "DownAppPlane", "FavGiftPlane", "Feedback", "FriendItem", "GoodFriend",
                                  "GoodNode", "HitEgg", "InviteGift", "LucklyRedEnvelope", "MainLayer", "NetReconnect",
                                  "NewbieGuide", "OrderItem", "PlayerHome", "PlayerLevelUp", "RecortItem",
                                  "ShareDiamond", "SoilBlock", "Task", "VegetealRecort", "WareHouse", "Windfall",
                                  "Withdraw"]

    def create(self):
        super(CodeAnalyse, self).create()
        # 解析proto的调用 -----------------------------------------------------------------------------------
        self.getSubClassObject("ProtoCodeAnalyse")
        self.protoCodeAnalyse.analyse()

        _sendList = self.protoCodeAnalyse._sendProtoNameList
        _onList = self.protoCodeAnalyse._onProtoNameList

        # 既有send，又有on
        for _send in _sendList:
            if _send.endswith("Req"):
                _on = _send.split("Req")[0] + "Res"
                if _on in _onList:
                    if not (_on in self.protoResAndReq):
                        self.protoResAndReq.append(_send)
                        self.protoResAndReq.append(_on)

        # 只有send，没有on，
        for _send in _sendList:
            if not _send in self.protoResAndReq:
                self.protoReq.append(_send)
        _tempProtoRes = []
        # 只有on，没有send
        for _on in _onList:
            if not _on in self.protoResAndReq:
                _tempProtoRes.append(_on)

        # Syn 起始的同步类
        for _on in _tempProtoRes:
            if _on.startswith("Syn"):
                self.protoSyn.append(_on)

        for _on in _tempProtoRes:
            if not _on in self.protoSyn:
                self.protoRes.append(_on)

        # 其他。。。
        self.protoOther = self.protoCodeAnalyse._otherProtoNameList

        if len(self.protoOther) > 0:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(), "所有的proto应当都是请求访问同步中的一种，不会有其他类型的存在")

        # 解析关联Prefab的js代码 附带所有js的分类 ----------------------------------------------------------------
        self.getSubClassObject("PrefabCombineJSAnalyse")

        # 挂载到Prefab或者fire上的Component文件。通过properties来获取，就是要确保他们都有properties属性
        self.prefabCombineJSAnalyse.analysePrefab()
        print("Prefab ---------------------------------")
        for _jsComponentFileShortName in self.prefabCombineJSAnalyse._jsComponentFileShortNameList:
            print(_jsComponentFileShortName)

        # 导出成模块的js
        self.prefabCombineJSAnalyse.analyseMoudleExports()
        print("module.exports -------------------------")
        for _jsModuleExportsFileShortName in self.prefabCombineJSAnalyse._jsModuleExportsFileShortNameList:
            print(_jsModuleExportsFileShortName)

        # 从全部js文件中对比 包含require
        self.prefabCombineJSAnalyse.anaylseShortJsNameAndRequireRelation()
        self.prefabCombineJSAnalyse.toDotDict("/Volumes/18604037792/develop/ShunYuan/")

        print("other ----------------------------------")
        for _jsAllShortName in self.prefabCombineJSAnalyse._jsAllShortNameList:
            if not (_jsAllShortName in self.prefabCombineJSAnalyse._jsComponentFileShortNameList):
                if not (_jsAllShortName in self.prefabCombineJSAnalyse._jsModuleExportsFileShortNameList):
                    print(_jsAllShortName)

        _componentRequireDict = {}
        _requireComponentDict = {}
        for _shortJsName, _requireList in self.prefabCombineJSAnalyse._requireDict.items():
            _justName = _shortJsName.split("/").pop().split(".js")[0]
            # 是一个组件的话
            if _justName in self.componentNameList:
                # 组件对其他js的引用是一个列表
                _componentRequireDict[_shortJsName] = []
                _requireList.sort()
                for _require in _requireList:
                    _requireShortName = self.prefabCombineJSAnalyse.getMoudleExportShortNameByJustName(_require)
                    if _requireShortName:
                        _requireRealName = _requireShortName
                    else:
                        _requireRealName = _require
                    _componentRequireDict[_shortJsName].append(_requireRealName)
                    if not (_requireRealName in _requireComponentDict.keys()):
                        _requireComponentDict[_requireRealName] = []
                    _requireComponentDict[_requireRealName].append(_shortJsName)

        # 组件 和 引用 的关系
        print("component -> require --------------------------------")
        for _shortComponentJsName, _requireList in _componentRequireDict.items():
            print("    " + _shortComponentJsName)
            _requireList.sort()
            for _requireShortName in _requireList:
                print("        " + _requireShortName)

        # 引用 和 组件 的关系
        print("require -> component --------------------------------")
        for _shortRequireJsName, _componentList in _requireComponentDict.items():
            print("    " + _shortRequireJsName)
            _componentList.sort()
            for _shortComponentJsName in _componentList:
                print("        " + _shortComponentJsName)

        # 将关系绘制成图
        self.toDotDict(
            _componentRequireDict,  # 组件 对应 引用 的 关系
            self.protoCodeAnalyse._jsProtoRelationDict,  # js代码 和 Protocol 的关系
            self.protoCodeAnalyse._allProtoNameList  # js代码中实际引用的Protocol
        )

    def toDotDict(self, componentRequireDict_: dict, jsProtoRelationDict_: dict, protoList_: list):
        _keyList = []
        _valueAllList = []
        _relationDictList = []
        _relationColorDict = {}
        _colorCurrentIdx = 0
        _colorList = [
            "blue",
            "blue4",
            "brown1",
            "brown4",
            "burlywood1",
            "burlywood4",
            "cadetblue1",
            "cadetblue4",
            "chartreuse1",
            "chartreuse4",
            "chocolate1",
            "chocolate4",
            "cornflowerblue",
            "darkslateblue",
            "dodgerblue4",
            "darkgreen",
            "darkseagreen4",
            "forestgreen",
            "black",
            "purple1",
            "purple3",
            "slateblue1",
            "slateblue3",
            "deepskyblue1",
            "deepskyblue4",
            "crimson",
            "lightsteelblue1",
            "lightsteelblue4",
            "aquamarine1",
            "aquamarine4",
        ]

        # 使用protobuf的js代码，也是Component或者是moudle.export
        for _key in jsProtoRelationDict_.keys():
            _justName = _key.split("/").pop().split(".js")[0]
            if _justName in self.componentNameList:
                if not (_key in _keyList):
                    _keyList.append(_key)
            else:
                if not (_key in _valueAllList):
                    _valueAllList.append(_key)

        for _key in componentRequireDict_.keys():
            _valueList = componentRequireDict_[_key]

            # 保存所有 _key
            _keyList.append(_key)
            for _value in _valueList:
                # 不是.js结尾的
                if not _value.endswith(".js"):
                    continue
                # 保存所有值
                if not (_value in _valueAllList):
                    _valueAllList.append(_value)

                # 建立关系，并根据目标配色
                _relationsDict = dict()
                _relationTo = '"' + _value.split("/").pop() + '"'
                if not (_relationTo in _relationColorDict):
                    # 关联颜色
                    if _colorCurrentIdx == len(_colorList):
                        _colorCurrentIdx = 0
                    _relationColorDict[_relationTo] = _colorList[_colorCurrentIdx]
                    _colorCurrentIdx += 1
                # 确认关系
                _relationsDict["to"] = _relationTo
                _relationsDict["from"] = '"' + _key.split("/").pop() + '"'
                _relationDictList.append(_relationsDict)

        _keyDict = {}
        for _key in _keyList:
            _keyArr = _key.split("/")
            if len(_keyArr) != 2:
                continue
            _folder = _keyArr[0]
            _file = _keyArr[1]
            if not (_folder in _keyDict):
                _keyDict[_folder] = []
            if not (_file in _keyDict[_folder]):
                _keyDict[_folder].append(_file)

        _valueDict = {}
        for _value in _valueAllList:
            _valueArr = _value.split("/")
            if len(_valueArr) != 2:
                continue
            _folder = _valueArr[0]
            _file = _valueArr[1]
            if not (_folder in _valueDict):
                _valueDict[_folder] = []
            if not (_file in _valueDict[_folder]):
                _valueDict[_folder].append(_file)

        _mapName = "relation"
        _dotPicFolder = "/Volumes/18604037792/develop/ShunYuan/"

        # 构成 dot 文件
        _dotStr = "digraph " + _mapName + " {\n"
        _dotStr += '  rankdir = LR;\n'
        _dotStr += '  splines = polyline;\n'
        _dotStr += 'size="50,50"; ratio=fill; node[fontsize=24];\n'

        for _folder, _fileList in _keyDict.items():
            _fileListStr = ""
            for _file in _fileList:
                _fileListStr += '"' + _file + '" [shape = note];'
            _dotStr += 'subgraph "cluster_' + _folder + '" { node [style=filled]; label="' + _folder + '"; ' + _fileListStr + ' };\n'

        for _folder, _fileList in _valueDict.items():
            _fileListStr = ""
            for _file in _fileList:
                _fileListStr += '"' + _file + '";'
            _dotStr += 'subgraph "cluster_' + _folder + '" { label="' + _folder + '"; ' + _fileListStr + ' };\n'

        _reqListStr = ""
        _resListStr = ""
        _synListStr = ""

        for _proto in protoList_:
            if _proto in self.protoReq:
                _reqListStr += _proto + ' [shape=rarrow, color = "blue" , fontcolor = "blue", fontcolor = "white"];'
            elif _proto in self.protoRes:
                _resListStr += _proto + ' [shape=larrow, color = "purple", fontcolor = "purple", fontcolor = "white"];'
            elif _proto in self.protoSyn:
                _synListStr += _proto + ' [shape=invhouse, color = "peru", fontcolor = "peru", fontcolor = "white"];'

        for _i in range(len(self.protoResAndReq)):
            if _i % 2 == 0:
                _protoName = self.protoResAndReq[_i].split("Req")[0]
                _dotStr += 'subgraph "cluster_' + _protoName + '" { label="' + _protoName + '"; node [style=filled]; ' + \
                           self.protoResAndReq[_i] + ' [shape = rarrow, color = "blue" , fontcolor = "white"]; ' + \
                           self.protoResAndReq[
                               _i + 1] + ' [shape = larrow, color = "purple" , fontcolor = "white"];' + ' };\n'

        _dotStr += 'subgraph "cluster_reqProto" { label="Req"; node [style=filled];' + _reqListStr + ' };\n'
        _dotStr += 'subgraph "cluster_resProto" { label="Res"; node [style=filled];' + _resListStr + ' };\n'
        _dotStr += 'subgraph "cluster_otherProto" { label="Other"; node [style=filled]; ' + _synListStr + ' };\n'

        for _i in range(len(_relationDictList)):
            _dot_trans_dict = _relationDictList[_i]
            _dotStr += "  " + _dot_trans_dict["from"] + " -> " + _dot_trans_dict["to"] + " [color = " + \
                       _relationColorDict[_dot_trans_dict["to"]] + "];\n"

        _dotStr += "\n"

        for _jsShortName, _protoInfo in jsProtoRelationDict_.items():
            _send = _protoInfo["send"]
            for _protoName in _send:
                _dotStr += '  "' + _jsShortName.split("/").pop() + '" -> ' + _protoName + ' [color = blue];\n'

            _onAndOff = _protoInfo["onAndOff"]
            for _protoName in _onAndOff:
                _dotStr += '  "' + _jsShortName.split("/").pop() + '" -> ' + _protoName + ' [color = green];\n'

            _onNotOff = _protoInfo["onNotOff"]
            for _protoName in _onNotOff:
                _dotStr += '  "' + _jsShortName.split("/").pop() + '" -> ' + _protoName + ' [color = red];\n'

        _dotStr += "}\n"
        _dotFilePath = _dotPicFolder + _mapName + ".dot"
        fileUtils.writeFileWithStr(_dotFilePath, _dotStr)
        _cmd = 'dot ' + _mapName + '.dot -T png -o ' + _mapName + '.png'
        print(_cmd)
        subprocess.Popen(_cmd, shell=True, cwd=_dotPicFolder)

    def destory(self):
        super(CodeAnalyse, self).destory()
