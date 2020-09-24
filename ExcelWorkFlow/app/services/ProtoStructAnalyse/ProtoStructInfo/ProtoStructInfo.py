#!/usr/bin/env python3
# Created by jiasy at 2019/3/4
from base.supports.Base.BaseInService import BaseInService
from utils import folderUtils
from utils import fileUtils
import re


class ProtoStructInfo(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(ProtoStructInfo, self).create()

    def destory(self):
        super(ProtoStructInfo, self).destory()

    # 解析 .proto 文件
    def getProtobufStructInfoDict(self, protoFolderPath_):
        _protoStructInfoDict = {}
        _filePathDict = folderUtils.getFilePathKeyValue(protoFolderPath_, [".proto"])
        for _k, _v in _filePathDict.items():
            _keyName = _k.split("/")[-1].split(".")[0]
            # 名称 -> 路径 关系输出
            # print(str(_keyName).ljust(15) + ":" + str(_v))
            _currentProtoInfo = self.getProtobufStructInfo(_keyName, _v)
            _protoStructInfoDict[_keyName] = _currentProtoInfo
            # 输出 proto 结构信息
            # print(str(json.dumps(_currentProtoInfo, indent=4, sort_keys=False, ensure_ascii=False)))
            # 输出 proto 结构的 json 结构样式
            # dictUtils.showDictStructure(_currentProtoInfo)
        return _protoStructInfoDict

    # 整理字符串格式
    def formatProtoStr(self, protoStr_: str):
        _protoStr = protoStr_
        # 整理空格行
        regex = r"\n(\s*)\n"
        while re.search(regex, _protoStr):
            _protoStr = re.sub(regex, r'\n', _protoStr)

        # 移除空白行
        regex = r"\n\n"
        while re.search(regex, _protoStr):
            _protoStr = re.sub(regex, r'\n', _protoStr)

        # //comment
        # message name[...]
        # ->
        # message name[...]//comment
        regex = r"^\t*//(.*)\n(\t*)message\s*([1-9a-zA-Z_]+)(.*)\n"
        _protoStr = re.sub(regex, r'\2message \3\4//\1\n', _protoStr)

        # message name{//comment
        # ->
        # message name //comment
        # {
        regex = r"(\t*)message\s*([1-9a-zA-Z_]+)\s*{\t*//(.*)\n"
        _protoStr = re.sub(regex, r'\1message \2 //\3\n\1{\n', _protoStr)

        # message name {
        # ->
        # message name
        # {
        regex = r"(\t*)message\s*([1-9a-zA-Z_]+)\t*{\t*\n"
        _protoStr = re.sub(regex, r'\1message \2\n\1{\n', _protoStr)

        # //comment
        # enum name[...]
        # ->
        # enum name[...]//comment
        regex = r"\n\t*//(.*)\n(\t*)enum\s*([1-9a-zA-Z_]+)(.*)\n"
        _protoStr = re.sub(regex, r'\n\2enum \3\4//\1\n', _protoStr)

        # enum name{//comment
        # ->
        # enum name //comment
        # {
        regex = r"(\t*)enum\s*([1-9a-zA-Z_]+)\t*{\t*//(.*)\n"
        _protoStr = re.sub(regex, r'\1enum \2 //\3\n\1{\n', _protoStr)

        # enum name {
        # ->
        # enum name
        # {
        regex = r"(\t*)enum\s*([1-9a-zA-Z_]+)\t*{\t*\n"
        _protoStr = re.sub(regex, r'\1enum \2\n\1{\n', _protoStr)

        return _protoStr

    # 去除非结构字符串
    def removeUnuseStr(self, protocolStr_):
        _lines = protocolStr_.split("\n")
        _isStructureStart = False
        # 匹配正则模式
        _tableReg = re.search(r'(message|enum)\s*([1-9a-zA-Z_]+)\s*', _lines[0])
        if _tableReg:
            _isStructureStart = True

        # 结构还没有开始的话，就一直删
        while not _isStructureStart:
            _lines.pop(0)
            _tableReg = re.search(r'(message|enum)\s*([1-9a-zA-Z_]+)\s*', _lines[0])
            if _tableReg:
                _isStructureStart = True

        for _i in range(len(_lines)):
            _lines[_i] = _lines[_i].strip()

        return "\n".join(_lines)

    # 去除注释
    def removeComment(self, protocolStr_: str):
        _lines = protocolStr_.split("\n")
        for _i in range(len(_lines)):
            _lines[_i] = _lines[_i].split("//")[0].strip()
        return "\n".join(_lines)

    # 去除属性注释的空白间隔
    def removePropertyCommentSpace(self, protocolStr_: str):
        _protoStr = protocolStr_
        regex = r";.*//(.*)\n"
        _protoStr = re.sub(regex, r';//\1\n', _protoStr)
        return _protoStr

    # 重新构建protobuf字符串结构，将嵌套部分提出来然后重新命名
    def reStructProtoStr(self, protocolStr_: str):
        _tableNameStackList: list = []  # 表结构嵌套的列表
        _tableLineStackList: list = []  # 表的行缓存
        _tableDict: dict = {}
        _protocolStr = protocolStr_.replace("\t", "\n")
        _lines = _protocolStr.split("\n")
        for _line in _lines:
            _tableReg = re.search(r'(message|enum)\s*([1-9a-zA-Z_]+).*', _line)
            if _tableReg:
                _tableName = _tableReg.group(2)
                _tableNameStackList.append(_tableName)
                if not len(_tableLineStackList) == len(_tableNameStackList):
                    _tableLineStackList.append([])

                _tableLineStackList[len(_tableLineStackList) - 1].append(_line)
            else:
                if _line == "}":
                    _tableLineStackList[len(_tableLineStackList) - 1].append(_line)
                    _tableName = _tableNameStackList[0]
                    if len(_tableNameStackList) > 1:
                        _tableName = ".".join(_tableNameStackList)
                    _tableDict[_tableName] = "\n".join(_tableLineStackList[len(_tableLineStackList) - 1])
                    _tableNameStackList.pop()
                    _tableLineStackList.pop()
                else:
                    # 需要嵌套加工
                    _propertyReg = re.search(r'\s*(required|optional|repeated)\s*([0-9a-z-A-Z_]+)\s*(.*)', _line)
                    if _propertyReg:
                        _dataType = _propertyReg.group(2)
                        # 不是基础数据类型
                        if not self.belongToService.isNormalProperty(_dataType):
                            # 是不是在本proto中创建的
                            for _currentTableName in _tableDict.keys():
                                _tableShortName = _currentTableName.split(".").pop()
                                # 最后一节的名称相同
                                if _tableShortName == _dataType:
                                    # 使用的就是本protobuf中定义的结构
                                    _dataType = _currentTableName
                                    _strList = _line.split(" ")
                                    _strList[1] = _currentTableName
                                    _line = " ".join(_strList)
                                    break
                    if len(_tableLineStackList) > 0:
                        _tableLineStackList[len(_tableLineStackList) - 1].append(_line)

        _tableLines = []
        # _tableNameDict = {}  # 长短名对应表
        # for _key in _tableDict.keys():
        #     _tableShortName = _key.split(".").pop()
        #     _tableNameDict[_tableShortName] = _key

        # 一定是在本文件创建的，所以，短写明可以找到长写名
        for _key, _value in _tableDict.items():
            # 表结构字符串分行
            _lines = _value.split("\n")
            # 长表名用逗号切一定能获取短表名
            _tableShortName = _key.split(".").pop()
            if _lines[0].find(_tableShortName) >= 0:
                # 如果，用短表名能切分第一行的话[第一行是带表明的]
                _strList = _lines[0].split(_tableShortName)
                # 用长表名替换端表名
                _lines[0] = _key.join(_strList)
            # for _i in range(len(_lines)):
            #     # 不是第一行才有可能是属性
            #     if _i != 0:
            #         # 需要嵌套加工
            #         _propertyReg = re.search(r'\s*(required|optional|repeated)\s*([0-9a-z-A-Z_]+)\s*(.*)', _lines[_i])
            #         if _propertyReg:
            #             _dataType = _propertyReg.group(2)
            #             # 不是基础类型
            #             if not self.belongToService.isNormalProperty(_dataType):
            #                 # 在长短名对应表中的话,替代掉
            #                 if _dataType in _tableNameDict:
            #                     regex = r'\s*(required|optional|repeated)\s*([0-9a-z-A-Z_]+)\s*(.*)'
            #                     _lines[_i] = re.sub(regex, r'\1 \2 \3', _lines[_i])

            # 将表结构字符串还原回去
            _tableDict[_key] = "\n".join(_lines)
            # 拼接到返回字符串中
            _tableLines.append(_tableDict[_key])

        return "\n".join(_tableLines)

    '''
    解析protobuf，返回这样的结构
        +--tableList [0]                             - 包含的表列表
        |      +--type
        |      +--propertyList [0]                   - 属性列表 
        |      |      +--propertyName                - 属性名
        |      |      +--needType                    - 需求类型
        |      |      +--dataType                    - 数据类型
        |      |      +--dataTypeExchange            - 数据类型需要转换的类型
        |      |      +--index                       - 序号
        |      |      +--common                      - 属性注释
        |      +--protoName                          - proto名称
        |      +--tableName                          - 表名称
        |      +--lowerTableName                     - 小写表名称
        |      +--common                             - 表注释
        +--fileName                                  - 文件名
    '''

    # 解析 protobuf 文件，生成对应的 json 结构，用来记录 protobuf 的结构信息
    def getProtobufStructInfo(self, keyName_: str, protoFilePath_: str):
        # 创建proto信息的字典对象
        _currentProto = dict()
        _currentProto["tableList"] = []
        _currentProto["fileName"] = keyName_
        _currentTableDict = None
        _lastLine = None
        # _maxPropertyNameLen: int = 0

        # 整理样式
        _content = fileUtils.readFromFile(protoFilePath_)
        _content = self.formatProtoStr(_content)
        _content = self.removeUnuseStr(_content)
        _content = self.removePropertyCommentSpace(_content)
        # print(protoFilePath_)
        _content = self.reStructProtoStr(_content)

        # 读取每一行内容
        _protoLines = _content.split("\n")
        # 循环proto的每一行
        for _lineIdx in range(len(_protoLines)):
            # 两面空格都去掉
            _line = str(_protoLines[_lineIdx]).strip()

            # 新table
            _tableReg = re.search(r'message\s*([1-9a-zA-Z_\.]+)\s*(//\s*(.*)|)', _line)
            if _tableReg:
                _currentTableDict = {}
                _currentTableDict["type"] = "table"
                _currentTableDict["propertyList"] = []  # 属性列表
                _currentTableDict["fileName"] = keyName_  # 所属文件
                _currentProto["tableList"].append(_currentTableDict)
                _currentTableDict["protoName"] = _tableReg.group(1)
                # print("    protoName = " + str(_currentTableDict["protoName"]))
                # _currentTableDict["tableName"] = _tableReg.group(1)
                # _currentTableDict["lowerTableName"] = _currentTableDict["tableName"].lower()
                if _tableReg.group(2):
                    _currentTableDict["common"] = _tableReg.group(2).split("//")[1].strip()
                else:
                    _currentTableDict["common"] = ""
                    if _lastLine:
                        _commonReg = re.search(r'\s*//\s*(.*)', _lastLine)
                        if _commonReg:
                            _currentTableDict["common"] = _commonReg.group(1)
            else:
                # table中属性
                _propertyReg = re.search(
                    r'\s*(required|optional|repeated)\s*([0-9a-z-A-Z_\.]+)\s*([0-9a-z-A-Z_]+)\s*=\s*(\d+)\s*;\s*(//\s*.*|)',
                    _line)
                if _propertyReg:
                    _currentProperty = {}
                    _currentProperty["propertyName"] = _propertyReg.group(3)
                    # if len(_currentProperty["propertyName"]) > _maxPropertyNameLen:
                    #     _maxPropertyNameLen = len(_currentProperty["propertyName"])
                    # print("        PropertyName = " + str(_currentProperty["propertyName"]))
                    _currentProperty["needType"] = _propertyReg.group(1)
                    _currentProperty["dataType"] = _propertyReg.group(2)

                    # # 暂时忽略bytes类型
                    # if _currentProperty["dataType"] != "bytes":
                    #     if self.belongToService.isNormalProperty(_currentProperty["dataType"]):
                    #         _currentProperty["dataTypeExchange"] = _currentProperty["dataType"]
                    #         # int64/int32 的 result 统一变成String
                    #         if _currentProperty["propertyName"] == "result":
                    #             if _currentProperty["dataTypeExchange"] == "bigint":
                    #                 _currentProperty["dataTypeExchange"] = "string"
                    #     else:
                    #         _currentProperty["dataType"] = _propertyReg.group(2)

                    _currentProperty["index"] = _propertyReg.group(4)
                    _currentProperty["common"] = ""

                    if _propertyReg.group(5):
                        _currentProperty["common"] = _propertyReg.group(5).split("//")[1].strip()

                    _currentTableDict["propertyList"].append(_currentProperty)
                else:
                    _enumReg = re.search(r'enum\s*([1-9a-zA-Z_\.]+)\s*(//\s*(.*)|)', _line)
                    if _enumReg:
                        _currentEnumDict = {}
                        _currentEnumDict["type"] = "enum"
                        _currentEnumDict["propertyList"] = []  # 属性列表
                        _currentEnumDict["fileName"] = keyName_  # 所属文件
                        _currentProto["tableList"].append(_currentEnumDict)
                        _currentEnumDict["protoName"] = _enumReg.group(1)
                        # print("    enumName = " + str(_currentEnumDict["protoName"]))
                        # _currentEnumDict["tableName"] = _enumReg.group(1)
                        # _currentEnumDict["lowerTableName"] = _currentEnumDict["tableName"].lower()
                    else:
                        _enumTypeReg = re.search(r'\t*([0-9a-z-A-Z_\.]+)\s*=\s*([0-9])\s*;\s*(//\s*(.*)|)', _line)
                        if _enumTypeReg:
                            _currentProperty = {}
                            _currentProperty["propertyName"] = _enumTypeReg.group(1)
                            _currentProperty["index"] = _enumTypeReg.group(2)
                            _currentProperty["common"] = ""
                            if _enumTypeReg.group(3):
                                _currentProperty["common"] = _enumTypeReg.group(3).split("//")[1].strip()
                            _currentEnumDict["propertyList"].append(_currentProperty)

            _lastLine = _line
            # print("_maxPropertyNameLen : " + str(_maxPropertyNameLen))
        return _currentProto
