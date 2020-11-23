#!/usr/bin/env python3
# Created by jiasy at 2020/11/23

from Excel.ExcelBaseInService import ExcelBaseInService
import os
import re
import sys
from utils import sysUtils
from utils import fileUtils
from utils import regUtils
from utils import fileCopyUtils
from utils import folderUtils


class AirTest(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "ClearCreateJpg": {  # 清理用来识别图像的截屏文件。
                "createJpgFolder": "用来识别图片的手机截屏存放文件夹",
            },
            "GetPngUseByCode": {  # 将代码中使用到的png图片获取到新文件夹。删除或备份png文件，将新文件夹下的文件拷贝回去，就做到了去除无用png。
                "projectFolder": ".air .py .png 所在的工程文件夹"
            }
        }

    def create(self):
        super(AirTest, self).create()

    def destory(self):
        super(AirTest, self).destory()

    def ClearCreateJpg(self, dParameters_):
        _createJpgFolderPath = sysUtils.folderPathFixEnd(dParameters_["createJpgFolder"])
        _jpgPathList = folderUtils.getFilterFilesInPath(_createJpgFolderPath, [".jpg"])
        for _i in range(len(_jpgPathList)):
            _jpgPath = _jpgPathList[_i]
            _jpgName = os.path.basename(_jpgPath)
            _jpgResult = re.search(r'(\d+).jpg', _jpgName)  # 纯数字名称，满足条件就删除
            if _jpgResult:
                fileUtils.removeExistFile(_jpgPath)

    def GetPngUseByCode(self, dParameters_):
        _projectFolderPath = sysUtils.folderPathFixEnd(dParameters_["projectFolder"])
        _airAndPyPathList = folderUtils.getFilterFilesInPath(_projectFolderPath, [".air", ".py"])
        # 匹配 r"tpl1606022416813.png" 这样的内容
        _groupReg = r"r\"(.*)\.png\""
        # 要拷贝的png文件名
        _pngPathList = []
        for _i in range(len(_airAndPyPathList)):
            _airAndPyPath = _airAndPyPathList[_i]
            _matchGroupList = regUtils.getMatchGroupStrList(_airAndPyPath, _groupReg)  # 得到匹配的group阵列
            for _j in range(len(_matchGroupList)):
                _pngNameWithOutSuffix = _matchGroupList[_j][0]
                _pngPath = _projectFolderPath + "/" + _pngNameWithOutSuffix + ".png"
                if not _pngPath in _pngPathList:  # 没有记录过，就记录
                    _pngPathList.append(_pngPath)
        fileCopyUtils.copyFilesToFolder(_pngPathList, _projectFolderPath + "tempPics/")


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称资源路径，对应的Excel不存在

    _functionName = "ClearCreateJpg"
    _parameterDict = {  # 所需参数
        "createJpgFolder": "/Volumes/18604037792/develop/AirTest/ROK/",
    }

    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        _parameterDict,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )

    _functionName = "GetPngUseByCode"
    _parameterDict = {  # 所需参数
        "projectFolder": "/Volumes/18604037792/develop/AirTest/ROK/",
    }

    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        _parameterDict,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )


    sys.exit(1)
    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
