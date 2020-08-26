#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
import os


# proto 数据结构 解析生成 Hive 的 SQL 文件
# proto 解析，生成描述协议的文档。
class ProtoStructAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        # self.protobufFolder = fileUtils.getPath(self.resPath, "protobuf")
        self.protobufFolder = "/Volumes/18604037792/develop/ShunYuan/protocol_farm/server/"
        # self._usedTableNameList = [
        #     "ShareHelpOthersReq",
        #     "AppJumpReq",
        #     "AdvertGetRewardReq",
        #     "PingMsgReq",
        #     "BuildingGatherReq",
        #     "BuildBuildingReq",
        #     "BuildingProductItemReq",
        #     "ForceAddFriendReq",
        #     "GetShareToGroupReq",
        #     "LoginReq",
        #     "CommonOpensReq",
        #     "SynShareToGroupReq",
        #     "SynMiniAdReq",
        #     "BindStateReq",
        #     "FriendPageInfoReq",
        #     "FriendStateReq",
        #     "FinishGuideReq",
        #     "GetInviteAvailablePrizeReq",
        #     "UserCanWithDrawReq",
        #     "MiniGameShareInfoReq",
        #     "MiniGameShareAwardReq",
        #     "SynWatchDogReq",
        #     "LookAroundOtherFarmReq",
        #     "FixNpcFarmInfoReq",
        #     "StealOtherItemReq",
        #     "StealFixNpcFarmReq",
        #     "StealRandomNpcFarmReq",
        #     "UserShareLevelReq",
        #     "SynAdvertReq",
        #     "TakeOtherHelpAwardReq",
        #     "NoteDetailReq",
        #     "RandomNpcFarmInfoReq",
        #     "GetMiniGameShareWindfall",
        #     "TaskHandleUpReq",
        #     "ErrorReportReq",
        #     "SmashGoldenEggReq",
        #     "UserTakeRedGiftReq",
        #     "BuyStrengthReq",
        #     "StoreHouseSellItemReq",
        #     "TaskDelReq",
        #     "TaskEndDelCDReq",
        #     "HelpProductItemReq",
        #     "HelpBuildBuildingReq",
        #     "RandomBoxHelpOpenReq",
        #     "GetMiniAdReward",
        #     "SynBuildingData",
        #     "BuildingUnLockRes",
        #     "SynFriendData",
        #     "AgreeAddFriendRes",
        #     "FriendStateRes",
        #     "SynUserGuideInfo",
        #     "FinishGuideRes",
        #     "NotifyNewGuideRes",
        #     "SynInviteFriendsInfo",
        #     "GetInviteAvailablePrizeRes",
        #     "SynNewInviteFriend",
        #     "SynInviteFriendInfoChange",
        #     "InputInviteCodeRes",
        #     "SynUserRedGiftInfo",
        #     "UserTakeRedGiftRes",
        #     "SynMiniGameShareWindfall",
        #     "BuildingProductItemRes",
        #     "BuildingGatherRes",
        #     "BuildBuildingFinishRes",
        #     "BuildingFinishProductRes",
        #     "BuildBuildingRes",
        #     "RecFriendStealItemRes",
        #     "HelpProductItemRes",
        #     "NotifySomeOneHelpProductItemRes",
        #     "SynUserData",
        #     "SynUserExpChange",
        #     "UserCanWithDrawRes",
        #     "SynSystemTime",
        #     "PingMsgRes",
        #     "SynAdvertRes",
        #     "KickOffRes",
        #     "LookAroundOtherFarmRes",
        #     "StealOtherItemRes",
        #     "BuyStrengthRes",
        #     "FixNpcFarmInfoRes",
        #     "StealFixNpcFarmRes",
        #     "StealRandomNpcFarmRes",
        #     "SynWatchDogRes",
        #     "SynUserLevelUp",
        #     "UserShareLevelRes",
        #     "NotifySomeoneHelpedRes",
        #     "ShareHelpOthersRes",
        #     "HelpBuildBuildingRes",
        #     "SynShareInfo",
        #     "TakeOtherHelpAwardRes",
        #     "CommonRes",
        #     "SynStoreHouseData",
        #     "SynStoreHouseItemChange",
        #     "SynStoreHouseMoneyChange",
        #     "StoreHouseSellItemRes",
        #     "SynNormalTaskData",
        #     "SynNewNormalTask",
        #     "TaskHandleUpRes",
        #     "SynGatherTaskData",
        #     "TaskDelRes",
        #     "TaskEndDelCDRes",
        #     "NoteDetailRes",
        #     "RecNewNoteRes",
        #     "RandomNpcFarmInfoRes",
        #     "SynUserWithDrawTimes",
        #     "UserWithDrawRes",
        #     "CommonOpensRes",
        #     "BindStateRes",
        #     "SynMiniAdRes",
        #     "SynShareToGroupRes",
        #     "SynGoldenEgg",
        #     "LoginRes",
        #     "MiniGameShareInfoRes",
        #     "MiniGameShareAwardRes",
        #     "SmashGoldenEggRes",
        #     "WatchAdSpeedUpReq",
        #     "BuildingFinishProductReq"
        # ]

        self._tableRequireByOtherList = []  # 被引用的表
        self._enumTableList = []  # 枚举表
        self._tableFullNameDict = {}  # 全名表结构，所有表
        self._mainTableShortNameList = []  # 实际使用的主表，刨除了被引用表
        self._tableNameReqAndResList = []  # 一去一回表
        self._tableNameReqList = []  # 有去无回表
        self._tableNameResList = []  # 有回无去表
        self._tableNameOther = []  # 非请求访问表

    def create(self):
        super(ProtoStructAnalyse, self).create()

        # 解析loho的proto结构
        self.getSubClassObject("ProtoStructInfo")
        self.getSubClassObject("ToHiveTableSQL")

        # 输出 构建 protol 结构
        self.buildProtoStructure(self.protobufFolder)
        #return

        # 输出文件夹内的所有 protol 结构
        self.expandTableStructureInFolder(self.protobufFolder)

        # # 将一个文件夹内的所有文件逐个解析，生成HiveSQL---------------------------------------------------------------
        # self.getHiveSQLByProtoFolder(self.protobufFolder)

        # # 将一个文件生成HiveSQL -------------------------------------------------------------------------------------
        # _tableSql = self.getHiveSQLByProtoPath(self.protobufFolder + "/battle.proto")
        # print('_tableSql = ' + str(_tableSql))

    def destory(self):
        super(ProtoStructAnalyse, self).destory()

    # proto 的基本类型
    def isNormalProperty(self, dataType_):
        return (dataType_ == "int64") or \
               (dataType_ == "int32") or \
               (dataType_ == "string") or \
               (dataType_ == "bool") or \
               (dataType_ == "float") or \
               (dataType_ == "double") or \
               (dataType_ == "bytes")

    # # 结构转换成一个dict
    # def protoStructureToDict(self,tableInfo_:dict):

    # 文件夹内的所有文件中的protobuf定义的表，放到一个大字典中。
    def getTableInfoDictFormFolder(self, protoFolderPath_: str):
        _protoStructInfoDict = {}
        _filePathDict = folderUtils.getFilePathKeyValue(protoFolderPath_, [".proto"])
        for _k, _v in _filePathDict.items():
            _keyName = _k.split("/")[-1].split(".")[0]
            _currentProtoInfo = self.protoStructInfo.getProtobufStructInfo(_k, _v)
            _protoStructInfoDict[_keyName] = _currentProtoInfo

        # 表字典
        _tableDict = {}
        for _protoName, _protoSturct in _protoStructInfoDict.items():
            _tableList = _protoSturct["tableList"]
            for _table in _tableList:
                _protoName = _table["protoName"]
                if _protoName in _tableDict:
                    self.raiseError(pyUtils.getCurrentRunningFunctionName(), "已经存在 : " + _protoName)
                _tableDict[_protoName] = _table
        return _tableDict

    def expandTableStructureInFolder(self, protobufFolder_: str):
        # 识别 文件夹 结构，按照文件夹的归属，输出proto分类和结构
        _folderList = folderUtils.getFolderListJustOneDepth(protobufFolder_)
        _folderList.sort()
        # 文件夹列表
        for _folder in _folderList:
            print(str(_folder) + " --------------------------------------------------------")
            _fileList = folderUtils.getFileListJustOneDepth(os.path.join(protobufFolder_, _folder), [".proto"])
            _fileList.sort()
            _mainTableFullNameInFolderList = []
            # 文件列表
            for _file in _fileList:
                for _tableFullName, _tableInfo in self._tableFullNameDict.items():
                    # 作为主表的才需要输出结构
                    if _tableFullName in self._mainTableShortNameList:
                        # 主表文件名一致，标示查找到
                        if _tableInfo["fileName"] == _file:
                            _mainTableFullNameInFolderList.append(_tableFullName)
                            break
            _baseStr = "        "
            _findBoo = False
            for _mainTableFullName in self._tableNameReqAndResList:
                if _mainTableFullName in _mainTableFullNameInFolderList:
                    _findBoo = True
                    break
            if _findBoo:
                print("    Req <-> Res ----------------------------------------")
                for _mainTableFullName in self._tableNameReqAndResList:
                    if _mainTableFullName in _mainTableFullNameInFolderList:
                        self.expandTableStructure(_mainTableFullName, 0, _baseStr)

            _findBoo = False
            for _mainTableFullName in self._tableNameReqList:
                if _mainTableFullName in _mainTableFullNameInFolderList:
                    _findBoo = True
                    break
            if _findBoo:
                print("    Req -> ---------------------------------------------")
                for _mainTableFullName in self._tableNameReqList:
                    if _mainTableFullName in _mainTableFullNameInFolderList:
                        self.expandTableStructure(_mainTableFullName, 0, _baseStr)

            _findBoo = False
            for _mainTableFullName in self._tableNameResList:
                if _mainTableFullName in _mainTableFullNameInFolderList:
                    _findBoo = True
                    break
            if _findBoo:
                print("    Res <- ---------------------------------------------")
                for _mainTableFullName in self._tableNameResList:
                    if _mainTableFullName in _mainTableFullNameInFolderList:
                        self.expandTableStructure(_mainTableFullName, 0, _baseStr)

            _findBoo = False
            for _mainTableFullName in self._tableNameOther:
                if _mainTableFullName in _mainTableFullNameInFolderList:
                    _findBoo = True
                    break
            if _findBoo:
                print("    Others ---------------------------------------------")
                for _mainTableFullName in self._tableNameOther:
                    if _mainTableFullName in _mainTableFullNameInFolderList:
                        self.expandTableStructure(_mainTableFullName, 0, _baseStr)

    # 展开表
    def expandTableStructure(self, tableName_: str, depth_: int = 0, baseStr_: str = ""):
        if not (tableName_ in self._tableFullNameDict):
            self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                            tableName_ + " 不存在，请校验。一般问题为文件内的结构是先使用后定义，导致无法找到结构定义")
        _tableInfo = self._tableFullNameDict[tableName_]
        _logStrList = []
        if depth_ == 0:
            _common = _tableInfo["common"]
            if not _common == "":
                _logStrList.append("{0}{1} // {2}".format(
                    baseStr_,
                    "|      " * (depth_ + 1),
                    _common
                ))
            _logStrList.append(baseStr_ +
                               "|      " * depth_ + tableName_ + " " + _tableInfo["fileName"])
        if _tableInfo["type"] == "table":
            if 'propertyList' in _tableInfo:
                _propertyList = _tableInfo["propertyList"]
                for _property in _propertyList:
                    _common = _property["common"]
                    if not _common == "":
                        _logStrList.append("{0}{1} // {2}".format(
                            baseStr_,
                            "|      " * (depth_ + 1),
                            _common
                        ))
                    _propertyName = _property["propertyName"]
                    _needType = _property["needType"]
                    _needTypeStr: str = ""
                    if _needType == "required":
                        _needTypeStr = "<!>"
                    elif _needType == "optional":
                        _needTypeStr = "<?>"
                    elif _needType == "repeated":
                        _needTypeStr = "[*]"
                    _dataType = _property["dataType"]
                    _index = _property["index"]

                    _logStrList.append("{0}{1}{2} {3} {4} {5}".format(
                        baseStr_,
                        "|      " * (depth_ + 1),
                        _index,
                        _needTypeStr,
                        _propertyName,
                        _dataType
                    ))
                    if not self.isNormalProperty(_dataType):
                        _subLogStrList = self.expandTableStructure(_dataType, (depth_ + 1), baseStr_)
                        for _subLogStr in _subLogStrList:
                            _logStrList.append(_subLogStr)
        else:
            if _tableInfo["type"] == "enum":
                if 'propertyList' in _tableInfo:
                    _propertyList = _tableInfo["propertyList"]
                    for _property in _propertyList:
                        _common = _property["common"]
                        if not _common == "":
                            _logStrList.append("{0}{1} // {2}".format(
                                baseStr_,
                                "|      " * (depth_ + 1),
                                _common
                            ))
                        _propertyName = _property["propertyName"]
                        _index = _property["index"]
                        _logStrList.append("{0}{1}{3} {2}".format(
                            baseStr_,
                            "|      " * (depth_ + 1),
                            _index,
                            _propertyName
                        ))
            else:
                _logStrList.append(baseStr_ + "|      " * (depth_ + 1) + " there is no properties... x")

        if depth_ == 0:
            _lenMax = 0
            # 整理格式
            for _i in range(len(_logStrList)):
                if _logStrList[_i].find("//") > 0:
                    continue
                _logStrSplitList = _logStrList[_i].split(" ")
                _logStrSplitList.pop()
                _logWithOutLast = " ".join(_logStrSplitList)
                _lenWithOutLast = len(_logWithOutLast)
                if _lenWithOutLast > _lenMax:
                    _lenMax = _lenWithOutLast
            _lenMax += 1
            _lastCommon = ""
            for _logStr in _logStrList:
                if _logStr.find("//") > 0:
                    _lastCommon = _logStr.split("//")[1]
                    continue

                _logStrSplitList = _logStr.split(" ")
                _logStrSplitLast = _logStrSplitList.pop()
                _logStrWithOutLast = ""
                if len(_logStrSplitList) > 1:
                    _logStrWithOutLast = " ".join(_logStrSplitList)
                else:
                    _logStrWithOutLast = _logStrSplitList[0]
                _newLogStr = _logStrWithOutLast + " " + (
                        _lenMax - len(_logStrWithOutLast)) * "-" + " " + _logStrSplitLast
                if _lastCommon == "":
                    print(_newLogStr)
                else:
                    print(_newLogStr + " // " + _lastCommon)
                    _lastCommon = ""

        return _logStrList

    def buildProtoStructure(self, protoFolderPath_: str):
        _tableDict = self.getTableInfoDictFormFolder(protoFolderPath_)

        for _shortTableName, _tableInfo in _tableDict.items():
            _protoName = _tableInfo["protoName"]
            self._tableFullNameDict[_protoName] = _tableInfo

        # 整理成全名字典
        for _tableFullName, _tableInfo in self._tableFullNameDict.items():
            _type = _tableInfo["type"]

            if _type == "enum":
                if not (_tableFullName in self._enumTableList):
                    self._enumTableList.append(_tableFullName)

            _common = ''
            if "common" in _tableInfo:
                _common = _tableInfo["common"]
            print("{0} [{1}] - {2}".format(_tableFullName, _type, _common))

            if _type == "table" and 'propertyList' in _tableInfo:
                _propertyList = _tableInfo["propertyList"]
                for _property in _propertyList:
                    _propertyName = _property["propertyName"]
                    _needType = _property["needType"]
                    _dataType = _property["dataType"]
                    _index = _property["index"]
                    _common = _property["common"]
                    if not self.isNormalProperty(_dataType):
                        if not (_dataType in self._tableRequireByOtherList):
                            self._tableRequireByOtherList.append(_dataType)
                    print(
                        "    {0} : {1}[{2}/{3}] - {4}".format(_index, _propertyName, _dataType, _needType,
                                                              _common))
            if _type == "enum" and 'propertyList' in _tableInfo:
                _propertyList = _tableInfo["propertyList"]
                for _property in _propertyList:
                    _propertyName = _property["propertyName"]
                    _index = _property["index"]
                    _common = _property["common"]
                    if not self.isNormalProperty(_dataType):
                        if not (_dataType in self._tableRequireByOtherList):
                            self._tableRequireByOtherList.append(_dataType)
                    print(
                        "    {0} : {1}[{2}/{3}] - {4}".format(_index, _propertyName, _dataType, _needType,
                                                              _common))

        print("被引用的proto文件 ----------------------------------------")
        for _tableRequireByOther in self._tableRequireByOtherList:
            print(str(_tableRequireByOther))

        print("为枚举的文件 ---------------------------------------------")
        for _enumTable in self._enumTableList:
            print(str(_enumTable))

        for _tableName, _tableInfo in self._tableFullNameDict.items():
            if not (_tableName in self._tableRequireByOtherList):
                if not (_tableName in self._enumTableList):
                    # if _tableName in self._usedTableNameList:  # js中使用了
                    self._mainTableShortNameList.append(_tableName)

        print("为主文件 ---------------------------------------------")
        self._mainTableShortNameList.sort()
        _reqTableList = []
        _resTableList = []

        for _tableName in self._mainTableShortNameList:
            if _tableName.endswith("Req"):
                _reqTableList.append(_tableName)
            elif _tableName.endswith("Res"):
                _resTableList.append(_tableName)
            else:
                self._tableNameOther.append(_tableName)

        for _tableNameReq in _reqTableList:
            _tableNameRes = _tableNameReq.split("Req")[0] + "Res"
            if _tableNameRes in _resTableList:
                self._tableNameReqAndResList.append(_tableNameReq)
                self._tableNameReqAndResList.append(_tableNameRes)

        for _tableNameReq in _reqTableList:
            if not _tableNameReq in self._tableNameReqAndResList:
                self._tableNameReqList.append(_tableNameReq)

        for _tableNameRes in _resTableList:
            if not _tableNameRes in self._tableNameReqAndResList:
                self._tableNameResList.append(_tableNameRes)

        print("    Req <-> Res ----------------------------------------")
        for _tableName in self._tableNameReqAndResList:
            print(_tableName)

        print("    Req -> ---------------------------------------------")
        for _tableName in self._tableNameReqList:
            print(_tableName)

        print("    Res <- ---------------------------------------------")
        for _tableName in self._tableNameResList:
            print(_tableName)

        print("    Others ---------------------------------------------")
        for _tableName in self._tableNameOther:
            print(_tableName)

    # 将一个proto文件转换成HiveTable的建表语句
    def getHiveSQLByProtoPath(self, protoPath_: str):
        _keyName = fileUtils.justName(protoPath_)
        _protoStructInfo = self.protoStructInfo.getProtobufStructInfo(_keyName, protoPath_)
        _tableSQL = self.toHiveTableSQL.protoStructInfoToHiveTableSQL(_protoStructInfo)
        return _tableSQL

    def getHiveSQLByProtoFolder(self, protoFolder_: str):
        # 获取 所有的 Proto结构信息
        _protoSturctInfoDict = self.protoStructInfo.getProtobufStructInfoDict(protoFolder_)
        # proto 文件名，proto 内的结构信息[表结构的列表]
        for _protoName, _protoStructInfo in _protoSturctInfoDict.items():
            _tableSQL = self.toHiveTableSQL.protoStructInfoToHiveTableSQL(_protoStructInfo)
            print('_tableSQL = \n' + str(_tableSQL))
