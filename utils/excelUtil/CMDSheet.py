# !/usr/bin/env python3
# json结构的复杂列表。
# 将Excel转换成字典，这里需要有类型指定。因为列表中有各种类型的对象混排时，类型判断会变得十分复杂。
# 通过前缀来判断类型。属性名大写。
import utils
from utils.excelUtil.DictSheet import DictSheet
from utils.excelUtil.Sheet import SheetType


class CMDSheet(DictSheet):
    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.CMD

    def toJsonDict(self):
        _processSteps = []
        for _currentRow in range(self.maxRow):
            _crValue = self.getStrByCr(0, _currentRow)
            if _crValue and not _crValue == "":
                _processStep = {"startRow": _currentRow}  # 步骤占格子信息
                if len(_processSteps) > 0:  # 当前行的开始，标志上一部分的结束
                    _processSteps[len(_processSteps) - 1]["endRow"] = _currentRow - 1
                _processSteps.append(_processStep)
        _processSteps[len(_processSteps) - 1]["endRow"] = self.maxRow  # 结束最后一个步骤信息
        _jsonDict = {  # 构建结构基础
            "dGlobalDict": self.getDict(  # 全局参数获取
                2, self.maxCol,
                _processSteps[0]["startRow"] + 1, _processSteps[0]["endRow"]
            ),
            "lProcessSteps": []
        }
        for _i in range(1, len(_processSteps)):  # 跳过第一个
            _jsonDict["lProcessSteps"].append(  # 添加步骤
                {
                    "dServiceInfo": {
                        "sBaseService": self.getStrByCr(0, _processSteps[_i]["startRow"]),
                        "sBaseInService": self.getStrByCr(1, _processSteps[_i]["startRow"]),
                        "sComment": self.getStrByCr(2, _processSteps[_i]["startRow"]),
                    },
                    "dParameters": self.getDict(  # 全局参数获取
                        2, self.maxCol,
                        _processSteps[_i]["startRow"] + 1, _processSteps[_i]["endRow"]
                    )
                }
            )
        return _jsonDict
