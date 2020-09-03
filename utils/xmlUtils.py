# !/usr/bin/env python3
import datetime
import re
import xml.etree.ElementTree as ET
import logging
from utils import folderUtils
from utils import fileUtils
import json
import os


# ------------------------------------xml 转换成 json 结构---------------------------------------------------------------------------------------
def xmlToJsonDict(path_: str):
    _xmlRoot = ET.parse(path_).getroot()
    _jsonDict = xmlNodeToJsonNode(_xmlRoot)
    return _jsonDict


# 一个xml的节点，转换成一个json的节点。
def xmlNodeToJsonNode(xmlNode_):
    _jsonNode = {}
    _jsonNode["__tag__"] = xmlNode_.tag
    for _attrKey in xmlNode_.attrib:
        _attrValue = xmlNode_.attrib[_attrKey]
        if _attrKey == "__tag__" or _attrKey == "__elements__":
            logging.error("xml 转换 json : __tag__ 和 __elements__ 为关键字")
        _jsonNode[_attrKey] = _attrValue
    _jsonNode["__elements__"] = []
    for _element in xmlNode_:
        _jsonNode["__elements__"].append(xmlNodeToJsonNode(_element))
    return _jsonNode


# xml转换成json格式
def xmlToJsonDictInFolderThenWrite(xmlFolderPath_: str, outputFolderPath_: str):
    folderUtils.makeSureDirIsExists(outputFolderPath_)
    _xmlPathToJsonContentDict = xmlToJsonDictInFolder(xmlFolderPath_)  # 获取 [路径:JSON内容] 字典
    for _xmlPath in _xmlPathToJsonContentDict:
        _jsonStr = str(json.dumps(_xmlPathToJsonContentDict[_xmlPath], indent=4, sort_keys=False, ensure_ascii=False))
        _targetJsonPath = os.path.join(
            outputFolderPath_,
            os.path.dirname(_xmlPath.split(xmlFolderPath_)[1]),
            fileUtils.justName(_xmlPath) + ".json"
        )
        print(str(_targetJsonPath))
        fileUtils.writeFileWithStr(
            _targetJsonPath,
            _jsonStr
        )


# 文件夹中的xml全部转换成json格式字典，驻留在内存中
def xmlToJsonDictInFolder(xmlFolderPath_: str) -> dict:
    _xmlPathList = folderUtils.getFilterFilesInPath(xmlFolderPath_, [".xml"])
    _xmlPathToJsonContentDict = {}  # 键是xml路径，值是json字典对象
    for _xmlPath in _xmlPathList:
        _xmlPathToJsonContentDict[_xmlPath] = xmlToJsonDict(_xmlPath)
    return _xmlPathToJsonContentDict  # 返回路径和内容的键值对


if __name__ == "__main__":
    xmlToJsonDictInFolderThenWrite(
        '/Volumes/18604037792/develop/ShunYuan/FGUI/Pyramid/assets/',
        '/Volumes/18604037792/develop/ShunYuan/FGUI/Pyramid/xmlToJson/'
    )
