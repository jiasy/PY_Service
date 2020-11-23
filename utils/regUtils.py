# !/usr/bin/env python3
import re
from utils import fileUtils
from utils import fileCopyUtils


# 获取匹配到的正则对象列表
def getMatchList(filePath_: str, regStr_: str, printBoo_: bool = False):
    _contentStr = fileUtils.readFromFile(filePath_)
    _matches = re.finditer(regStr_, _contentStr, re.MULTILINE)
    _matchList = []
    for _matchNum, _match in enumerate(_matches, start=1):
        if printBoo_:
            print("Match {matchNum} was found at {start}-{end}: {match}".format(
                matchNum=_matchNum,
                start=_match.start(),
                end=_match.end(),
                match=_match.group()
            )
            )
        for _groupNum in range(0, len(_match.groups())):
            _groupNum = _groupNum + 1
            if printBoo_:
                print("Group {groupNum} found at {start}-{end}: {group}".format(
                    groupNum=_groupNum,
                    start=_match.start(_groupNum),
                    end=_match.end(_groupNum),
                    group=_match.group(_groupNum)
                )
                )
        _matchList.append(_match)
    return _matchList


# 满足表达式的字符串列表
def getMatchStrList(filePath_: str, regStr_: str):
    _matchList = getMatchList(filePath_, regStr_)
    _matcheStrList = []
    for _i in range(len(_matchList)):
        _match = _matchList[_i]
        _matcheStrList.append(_match.group())
    return _matcheStrList


# 满足表达式的匹配列表(二维数组，一维匹配，二维分组)
def getMatchGroupStrList(filePath_: str, regStr_: str):
    _matchList = getMatchList(filePath_, regStr_)
    _matchGroupList = []
    for _i in range(len(_matchList)):
        _match = _matchList[_i]
        _groupList = []
        for _groupNum in range(0, len(_match.groups())):
            _groupList.append(_match.group(_groupNum + 1))
        _matchGroupList.append(_groupList)
    return _matchGroupList


if __name__ == "__main__":
    _airTestFolder = "/Volumes/18604037792/develop/AirTest/"
    _projectName = "ROK"

    # 匹配 r"tpl1606022416813.png" 这样的内容
    _groupReg = r"r\"(.*)\.png\""
    # 得到匹配的group阵列
    _matchGroupList = getMatchGroupStrList(_airTestFolder + _projectName + "/" + "checkInCity.py", _groupReg)

    _filePathList = []
    for _i in range(len(_matchGroupList)):
        _filePathList.append(_airTestFolder + _projectName + "/" + _matchGroupList[_i][0] + ".png")

    fileCopyUtils.copyFilesToFolder(_filePathList, _airTestFolder + "pics/")
