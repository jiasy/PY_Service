# !/usr/bin/env python3
# 键值对，平表配置。
# 一般是配置总汇，同一套键值对，可能有不同的配置。比如:
#       同一个app的多个环境的不同配置。
#           本机开发，内网测试，外网测试，仿真环境，真实环境。
#       同一个IOS/APK工程，嵌入不同的游戏。维护一个打包工程，通过脚本构建修改参数，拷贝内容来切换游戏。
#           同一套SDK的不同参数，资源的不同Git地址等等。
#       同一个app的多国语言
#
# 通过列名来划分分组
#       每出现一个分组，会创建一个文件夹。
#           每列的参数，会写入这个文件夹下Sheet同名文件内
# 如果，字段为空的话。必须写入 - 值，标示当前参数为空
#       因为，判断条件是 != ""，所以当第一个类目的某个字段为 ""，会认为当前行没有数据，所以，用 - 来标示空数据
import utils
import os
import json
from utils.excelUtil.Sheet import Sheet
from utils.excelUtil.Sheet import SheetType


class KVSheet(Sheet):
    def __init__(self):
        super().__init__()
        self.sheetType = SheetType.KV

    # 覆盖掉sheet直接写入文件的方法。替换成，按照类目的文件夹做二级分类的形式。
    def toJsonFile(self, locateFolderPath_: str):
        _jsonDict = self.toJsonDict()
        for _classifyName in _jsonDict:
            _jsonFilePath = os.path.join(locateFolderPath_, _classifyName, self.sheetName + ".json")
            utils.fileUtils.writeFileWithStr(
                _jsonFilePath,
                str(json.dumps(_jsonDict[_classifyName], indent=4, sort_keys=False, ensure_ascii=False))
            )

    # KeyValue ------------------------------------------------------------------------------------
    def toJsonDict(self):
        _sheetDict = {}
        for _rowStart in range(self.maxRow):  # 第一个，从列3->列5全有值的，为第一行数据。其他不满足的都是Excel用来显示的标题/注释
            if self.isRowContainsData(_rowStart):  # 当前行是数据行，就开始数据记录
                for _colNum in range(4, self.maxCol):  # 取得 每一列的内容
                    _classifyName = self.getStrByCr(_colNum, _rowStart)  # 取得 每一列的名称，列名对应后来生成的文件夹[分类]
                    if _classifyName and _classifyName != "":
                        _configDict = {}
                        _sheetDict[_classifyName] = _configDict
                        for _rowNum in range(_rowStart + 1, self.maxRow):  # 取得键值
                            if self.isRowContainsData(_rowNum):  # 当前行是数据行，进行数据录入
                                _valueStr = self.getStrByCr(_colNum, _rowNum)
                                if _valueStr == "":  # 纯空报错
                                    raise utils.pyUtils.AppError(
                                        "类目必须填写 - 标示空数据 " + self.sheetName +
                                        " -> " + _classifyName +
                                        " : " + utils.excelUtils.crToPos(_colNum, _rowNum)
                                    )
                                elif _valueStr != "-":  # 不是空数据，就录入
                                    _configDict[self.getStrByCr(3, _rowNum)] = self.getStrByCr(_colNum, _rowNum)
                    else:
                        break
                break
        return _sheetDict

    def isRowContainsData(self, rowNum_):
        if self.getStrByCr(2, rowNum_) != "" and \
                self.getStrByCr(3, rowNum_) != "" and \
                self.getStrByCr(4, rowNum_) != "":
            return True
        else:
            return False