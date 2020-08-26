# !/usr/bin/env python3
import os


# 通过当前模块的完整路径，获取对应的资源路径。这样做到，资源和代码结构一致
def getRestPathForFullClassPath(appResPath_, fullClassPath_):
    _fullClassPathStrArr = fullClassPath_.split(".")
    _fullResPath = appResPath_
    # 从第三个元素开始，
    # 第一个元素是 APPName 为所属的文件夹。
    # 第二个元素是 app 被 res 文件夹同级替换。
    for _i in range(2, len(_fullClassPathStrArr)):
        _item = _fullClassPathStrArr[_i]
        _fullResPath = os.path.join(_fullResPath, _item)
    return _fullResPath
