#!/usr/bin/env python3
# Created by jiasy at 2019/3/4
from base.supports.Base.BaseInService import BaseInService
from utils import fileUtils
import time


# 一次解析一个 protobuf 的 结构信息
class ToHiveTableSQL(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        # 读取 SQL 模板 内容。
        self._sqlTemplete = fileUtils.readFromFile(
            fileUtils.getPath(
                self.belongToService.resPath,
                "HiveSql/SqlTemplete"
            )
        )

    def create(self):
        super(ToHiveTableSQL, self).create()

    def destory(self):
        super(ToHiveTableSQL, self).destory()

    # 类型转换，基础类型 转换成 Hive SQL 的时候，字符串需要变更一下
    def dataTypeExchange(self, dataType_):
        if dataType_ == "int64": return "bigint"
        if dataType_ == "int32": return "bigint"
        if dataType_ == "string": return "string"
        if dataType_ == "bool": return "boolean"
        if dataType_ == "float": return "float"
        if dataType_ == "double": return "double"
        if dataType_ == "bytes": return "binary"

    # proto 的基本类型
    def isNormalProperty(self, dataType_):
        return (dataType_ == "int64") or \
               (dataType_ == "int32") or \
               (dataType_ == "string") or \
               (dataType_ == "bool") or \
               (dataType_ == "float") or \
               (dataType_ == "double") or \
               (dataType_ == "bytes")

    # 从proto信息列表中获取到对应这个表名的信息
    def getTableDictByName(self, tableList_, tableName_):
        for _i in range(len(tableList_)):
            if tableList_[_i]["tableName"] == tableName_:
                return tableList_[_i]

    # 模板替换
    def getSQLTableStr(self, templeteStr_, tableDict_: dict):
        return templeteStr_.format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            tableDict_["tableName"],
            tableDict_["propertySQLStr"],
            tableDict_["common"],
            tableDict_["protoName"]
        )

    # 创建嵌套结构
    def createNestedTableStr(self, tableList_, tableName_, loopTimes_):
        _tabSpace = ""
        for _i in range(loopTimes_):
            _tabSpace += "    "

        _tableDict = self.getTableDictByName(tableList_, tableName_)
        _propertySQLStr = ""
        _propertyLength = len(_tableDict["propertyList"])
        for _propertyIdx in range(_propertyLength):
            _currentProperty = _tableDict["propertyList"][_propertyIdx]
            if self.belongToService.isNormalProperty(_currentProperty["dataType"]):  # 非嵌套
                if _currentProperty["needType"] == "repeated":
                    _propertySQLStr += _tabSpace + _currentProperty["propertyName"] + ":array<" + _currentProperty[
                        "dataTypeExchange"] + ">"
                else:
                    _propertySQLStr += _tabSpace + "`{0}`:{1}".format(_currentProperty["propertyName"],
                                                                      _currentProperty["dataTypeExchange"])
                # 追加 换行
                if not _propertyIdx == (_propertyLength - 1):
                    _propertySQLStr += ", --" + _currentProperty["common"] + "\n"
                else:  # 最后一行没 逗号
                    _propertySQLStr += " -- " + _currentProperty["common"]

            else:  # 嵌套
                # 另外一个表,表名
                _otherTableName = _currentProperty["dataType"]
                # 另外一个表,数据信息
                _otherTableDict = self.getTableDictByName(tableList_, _otherTableName)
                # 另一个表是 table 而不是 enum
                if _otherTableDict["type"] == "table":
                    # 结构体前缀
                    if _currentProperty["needType"] == "repeated":
                        _propertySQLStr += _tabSpace + "`{0}`:array<struct<".format(_currentProperty["propertyName"])
                    else:
                        _propertySQLStr += _tabSpace + "`{0}`:struct<".format(_currentProperty["propertyName"])

                    # 获取所使用的零一个表结构名
                    _propertySQLStr += ' -- ' + _otherTableName + " " + \
                                       self.getTableDictByName(tableList_, _otherTableName)[
                                           "common"] + "\n"

                    # 结构体内容
                    _propertySQLStr += _tabSpace + self.createNestedTableStr(tableList_, _otherTableName,
                                                                             loopTimes_ + 1) + "\n"

                    # 结构体后缀
                    if _currentProperty["needType"] == "repeated":
                        _propertySQLStr += _tabSpace + ">>\n"
                    else:
                        _propertySQLStr += _tabSpace + ">\n"

                    # 追加 换行
                    if not _propertyIdx == (_propertyLength - 1):
                        _propertySQLStr += _tabSpace + ",\n"
                elif _otherTableDict["type"] == "enum":
                    # 枚举类型，转换int写法，枚举类型只能是 optional/required 的
                    _propertySQLStr += _tabSpace + "`{0}`:{1}".format(_currentProperty["propertyName"], "bigint")
                    # 追加 换行
                    if not _propertyIdx == (_propertyLength - 1):
                        _propertySQLStr += ", --" + _currentProperty["common"] + "\n"
                    else:  # 最后一行没 逗号
                        _propertySQLStr += " -- " + _currentProperty["common"]

        return _propertySQLStr

    # proto的结构信息 转换成  Hive SQL
    def protoStructInfoToHiveTableSQL(self, protoStructInfo: dict):
        _tableList = protoStructInfo["tableList"]
        _SQLStr = ""
        for _tableIdx in range(len(_tableList)):
            # 循环每一个结构
            _currentTableDict = _tableList[_tableIdx]
            # table 类型的才需要进行结构解析
            if _currentTableDict["type"] == "table":
                # 每一个表的属性构成的字符串
                _currentTableDict["propertySQLStr"] = ""
                for _propertyIdx in range(len(_currentTableDict["propertyList"])):
                    _currentProperty = _currentTableDict["propertyList"][_propertyIdx]
                    if self.belongToService.isNormalProperty(_currentProperty["dataType"]):  # 非嵌套
                        # 是否是循环数组
                        if _currentProperty["needType"] == "repeated":
                            _currentTableDict["propertySQLStr"] += ",`{0}` array<{1}>".format(
                                _currentProperty["propertyName"],
                                _currentProperty["dataTypeExchange"])
                        else:
                            _currentTableDict["propertySQLStr"] += ",`{0}` {1}".format(
                                _currentProperty["propertyName"],
                                _currentProperty[
                                    "dataTypeExchange"])
                        # 补充注释
                        if _currentProperty["common"] == "":
                            _currentTableDict["propertySQLStr"] += "\n"
                        else:
                            _currentTableDict["propertySQLStr"] += ' comment \'' + _currentProperty[
                                "common"] + "\'\n"
                    else:  # 嵌套
                        # 另外一个表,表名
                        _otherTableName = _currentProperty["dataType"]
                        # 另外一个表,数据信息
                        _otherTableDict = self.getTableDictByName(_tableList, _otherTableName)
                        # 另一个表是 table 而不是 enum
                        if _otherTableDict["type"] == "table":
                            # 起始结构
                            if _currentProperty["needType"] == "repeated":
                                _currentTableDict["propertySQLStr"] += ",`{0}` array<struct<".format(
                                    _currentProperty["propertyName"])
                            else:
                                _currentTableDict["propertySQLStr"] += ",`{0}` struct<".format(
                                    _currentProperty["propertyName"])
                            # 添加结构注释，来自哪个表
                            _currentTableDict["propertySQLStr"] += ' -- ' + _otherTableName + "\n"

                            # 结构内容
                            _tempPropertyStr = self.createNestedTableStr(_tableList, _otherTableName, 1)
                            _currentTableDict["propertySQLStr"] += _tempPropertyStr
                            _currentTableDict["propertySQLStr"] += "\n"

                            # 收尾结构
                            if _currentProperty["needType"] == "repeated":
                                _currentTableDict["propertySQLStr"] += ">>"
                            else:
                                _currentTableDict["propertySQLStr"] += ">"

                            # 补充注释
                            if _currentProperty["common"] == "":
                                _currentTableDict["propertySQLStr"] += "\n"
                            else:
                                _currentTableDict["propertySQLStr"] += ' comment \'' + _currentProperty[
                                    "common"] + "\'\n"
                        elif _otherTableDict["type"] == "enum":
                            # 枚举类型，转换int写法，枚举类型只能是 optional/required 的
                            _currentTableDict["propertySQLStr"] += ",`{0}` {1}".format(
                                _currentProperty["propertyName"], "bigint")
                            # 补充注释
                            if _currentProperty["common"] == "":
                                _currentTableDict["propertySQLStr"] += "\n"
                            else:
                                _currentTableDict["propertySQLStr"] += ' comment \'' + _currentProperty[
                                    "common"] + "\'\n"

                _tableStr = self.getSQLTableStr(self._sqlTemplete, _currentTableDict)
                _SQLStr += _tableStr
        return _SQLStr
