# !/usr/bin/env python3
# json结构的复杂列表。
# 将Excel转换成字典，这里需要有类型指定。因为列表中有各种类型的对象混排时，类型判断会变得十分复杂。
# 通过前缀来判断类型。属性名大写。
from utils.excelUtil.DictSheet import DictSheet
from utils.excelUtil.Sheet import SheetType


class CMDSheet(DictSheet):
    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.CMD

    def toJsonDict(self):
        _processSteps = []
        print(" " * 8 + " Sheet结构 解析中 ...")
        for _currentRow in range(self.maxRow):
            _crValue = self.getStrByCr(0, _currentRow)
            if _crValue and not _crValue == "":
                _processStep = {"startRow": _currentRow}  # 步骤占格子信息
                if len(_processSteps) > 0:  # 当前行的开始，标志上一部分的结束
                    _processSteps[len(_processSteps) - 1]["endRow"] = _currentRow - 1
                _processSteps.append(_processStep)
        _processSteps[len(_processSteps) - 1]["endRow"] = self.maxRow  # 结束最后一个步骤信息
        print(" " * 8 + " Sheet结构 解析完成")
        print(" " * 8 + " dGlobalDict 解析完成")
        print(" " * 8 + " dGlobalDict 解析中 ...")
        _jsonDict = {  # 构建结构基础
            "dGlobalDict": self.getDict(  # 全局参数获取
                2, self.maxCol,
                _processSteps[0]["startRow"] + 1, _processSteps[0]["endRow"]
            ),
            "lProcessSteps": []
        }
        print(" " * 8 + " dGlobalDict 解析完成")
        print(" " * 8 + " 步骤 解析中 ...")
        for _i in range(1, len(_processSteps)):  # 跳过第一个
            _baseServiceName = self.getStrByCr(0, _processSteps[_i]["startRow"])
            _baseInServiceName = self.getStrByCr(1, _processSteps[_i]["startRow"])
            _functionName = self.getStrByCr(2, _processSteps[_i]["startRow"])
            _printStr = " " * 12 + "步骤 [" + str(_i) + "/" + str(len(_processSteps) - 1) + "] "
            _printStr += _baseServiceName + ":" + _baseInServiceName + " -> " + _functionName + "开始解析"
            print(_printStr)  # 输出步骤
            _jsonDict["lProcessSteps"].append(  # 添加步骤
                {
                    "dServiceInfo": {
                        "sBaseService": _baseServiceName,  # 服务名
                        "sBaseInService": _baseInServiceName,  # 子服务名
                        "sFunctionName": _functionName,  # 功能名
                        "sComment": self.getStrByCr(1, _processSteps[_i]["startRow"] + 1),  # 子服务名下一格，对应的注释
                    },
                    "dParameters": self.getDict(  # 全局参数获取
                        2, self.maxCol,  # 第三列开始，就是参数
                        _processSteps[_i]["startRow"] + 2, _processSteps[_i]["endRow"],  # 一行给服务指定，一行给注释，所以+2
                    )
                }
            )
            print(" " * 12 + "步骤 [" + str(_i) + "/" + str(len(_processSteps) - 1) + "] 解析完成")
        return _jsonDict
