#!/usr/bin/env python3
# Created by jiasy at 2020/11/2

from Excel.ExcelBaseInService import ExcelBaseInService
import os
from utils import sysUtils
from utils import folderUtils
from utils import pyUtils
from PIL import Image


class IconResize(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "IconResize": {
                "sourceFolder": "用来放缩的图片文件夹，文件可能有多个。不同尺寸查找对应自己的那张进行放缩。",
                "targetFolder": "将图片生成到哪里？",
                "sizeList": "目标大小列表",
                "type": "图片格式: .jpg 和 .png 中的一种",
            },
        }

    def create(self):
        super(IconResize, self).create()

    def destory(self):
        super(IconResize, self).destory()

    def IconResize(self, dParameters_):
        _sourceFolder = sysUtils.folderPathFixEnd(dParameters_["sourceFolder"])
        _targetFolder = sysUtils.folderPathFixEnd(dParameters_["targetFolder"])
        _sizeList = dParameters_["sizeList"]
        _targetType = dParameters_["type"]
        _sourcePicList = folderUtils.getFilterFilesInPath(_sourceFolder, [".jpg", ".png"])
        
        _imList = []  # image信息列表
        for _sourcePicPath in _sourcePicList:  # 要放缩的Icon
            _im = Image.open(_sourcePicPath)  # 加载内存，方便获取信息
            _sizeCompareValue = _im.width / _im.height
            if _sizeCompareValue > 1.1 or _sizeCompareValue < 0.9:  # 校验宽高比，差太多提示一下
                self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                _sourcePicPath + " 作为图标，宽高比相差有点儿大")
            _imList.append(_im)
        _imList.sort(key=lambda _im: _im.width, reverse=True)  # 按照由大到小的顺序
        _sizeList.sort(key=lambda _size: _size, reverse=True)  # 由大到小

        if _sizeList[0] > _imList[0].width:
            self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                            "索取大小的最大值(" + str(_sizeList[0]) + ")大于给与大小的最大值(" + str(_imList[0].width) + ")")

        # Image实例.thumbnail((宽, 高))会改变Image实例本身，所以，又大到小进行逐步变化。
        # 由大到小的，将每一个小于自己尺寸的ICON生成一遍。小的会覆盖大的生成的ICON，最后达到想要的结果。
        for _im in _imList:  # 先比大的，后比小的，小于等于最接近的会最后成为目标图片
            for _size in _sizeList:  # 放缩的目标值
                if _size <= _im.width:  # 目标值小于当前图片的大小。就使用者张图
                    _targetIconPath = os.path.join(_targetFolder, 'Icon-' + str(_size) + _targetType)
                    _im.thumbnail((_size, _size))  # target Image 在内存内存中大小会变小，下一个循环比他要小。所以，_sizeList必须是倒叙的
                    if _targetType == ".png":
                        _im.save(_targetIconPath)
                    elif _targetType == ".jpg":
                        _im.save(_targetIconPath, quality=95, subsampling=0)
                    else:
                        self.raiseError(pyUtils.getCurrentRunningFunctionName(),
                                        _targetType + " 格式无效，目标格式，只能是.png和.jpg中的一种")


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    _functionName = "IconResize"
    _parameterDict = {  # 所需参数
        "sourceFolder": "/Volumes/Files/develop/selfDevelop/Swift/AllTest/icon/sourceIcons/",
        "targetFolder": "/Volumes/Files/develop/selfDevelop/Swift/AllTest/icon/targetIcons/",
        "sizeList": [16, 20, 29, 32, 40, 58, 60, 64, 76, 80, 87, 120, 128, 152, 167, 180, 256, 512, 1024],  # IOS + MAC
        "type": ".jpg",
    }

    # Main.excelProcessStepTest(
    #     _baseServiceName,
    #     _subBaseInServiceName,
    #     _functionName,
    #     _parameterDict,
    #     {  # 命令行参数
    #         "executeType": "单体测试"
    #     }
    # )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
