# !/usr/bin/env python3
# 状态机配置表，从一个状态到另一个状态
from utils.excelUtil.Sheet import Sheet
from utils.excelUtil.Sheet import SheetType
from utils import fileUtils
from utils import cmdUtils
from utils import pyUtils
from utils import strUtils
import os


class StateSheet(Sheet):
    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.STATE

    def toJsonFile(self, locateFolderPath_: str):
        super().toJsonFile(locateFolderPath_)
        self.toDotPng(locateFolderPath_)  # 同时，制作一张状态图

    # 从左面状态如何去上面的状态
    def toJsonDict(self):
        _stateInfoDict = {"stateList": [], "transitions": [], "init": self.getStrByCr(1, 0)}
        for _col in range(self.maxCol - 2):  # 左上角第二个格子忽略，它为初始化状态。
            if not self.getStrByCr(_col + 2, 0) == self.getStrByCr(1, 1 + _col):
                raise pyUtils.AppError( self.sheetName + " : 行列对应值应当相同 ")
            else:
                _currentStateName = self.getStrByCr(_col + 2, 0)
                _stateInfoDict["stateList"].append(_currentStateName)

        for _col in range(2, self.maxCol):  # 解析出状态名
            _currentStateName = self.getStrByCr(_col, 0)  # 从哪里来
            for _row in range(1, self.maxRow):  # 解析状态名
                _targetStateName = self.getStrByCr(1, _row)  # 到哪里去
                _transName = self.getStrByCr(_col, _row)  # 交叉点为驱动事件名
                if _transName != "" and _currentStateName != _targetStateName:  # 转换名称 不是空，去往一个状态
                    # 变换名 _transName 驱动 从 _currentStateName 到 _targetStateName 的状态变更。
                    _stateTransDict = {"name": _transName, "to": _currentStateName, "from": _targetStateName}
                    _stateInfoDict["transitions"].append(_stateTransDict)
        return _stateInfoDict

    def toDotPng(self, outputFolderPath_: str):
        _stateInfoDict = self.toJsonDict()
        # 构成 dot 文件
        _dot_state_str = "digraph " + self.sheetName + " { " + _stateInfoDict["init"] + " [shape = Msquare]\n"
        for _i in range(len(_stateInfoDict["stateList"])):
            _dot_state_str = _dot_state_str + _stateInfoDict["stateList"][_i] + " \n"
        for _i in range(len(_stateInfoDict["transitions"])):
            _dot_trans_dict = _stateInfoDict["transitions"][_i]
            _dot_state_str = _dot_state_str + _dot_trans_dict["from"] + \
                             " -> " + _dot_trans_dict["to"] + \
                             " [ label= " + _dot_trans_dict["name"] + " ]" + " \n"
        _dot_state_str = _dot_state_str + "}"
        # 生成dot 给 可视化 用
        _targetDotPath = os.path.join(outputFolderPath_, self.sheetName + ".dot")
        _targetPngPath = os.path.join(outputFolderPath_, self.sheetName + ".png")
        fileUtils.writeFileWithStr(_targetDotPath, _dot_state_str)
        _graphCmd = "dot '" + _targetDotPath + "' -T png -o '" + _targetPngPath + "'"
        cmdUtils.doStrAsCmd(_graphCmd, outputFolderPath_, True)
