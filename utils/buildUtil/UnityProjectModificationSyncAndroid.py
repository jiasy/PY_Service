# !/usr/bin/env python3
import os
import shutil


# 前置工作
# Unity 构建一次 Android Project。为 finalProjectFolder
# Unity 中去掉所有 Android 对工程的修改，比如 Plugins/Android 文件夹。
# Unity 再次构建 Android Project。为 modificationFolder
# 将 modificationFolder 中的 Assets 的内容复制到 finalProjectFolder 中

class UnityProjectModificationSyncAndroid(object):
    def __init__(self,
                 modificationFolder_: str,  # 变更Unity后，打的新包
                 finalProjectFolder_: str  # 谁复制到哪里后，在应用修改
                 ):
        # assets 相对路径 Unity 2019
        _assetsPath = "unityLibrary/src/main/assets"
        _finalProjectAssetsPath = finalProjectFolder_ + _assetsPath
        _modificationFolderAssetsPath = modificationFolder_ + _assetsPath
        # 将 Assets 替换成新的
        if os.path.exists(_finalProjectAssetsPath):
            shutil.rmtree(_finalProjectAssetsPath)
        shutil.copytree(_modificationFolderAssetsPath, _finalProjectAssetsPath)


if __name__ == "__main__":
    _testProjectFolder = "/Volumes/18604037792/develop/ShunYuan/tolua_Build_Project/Android_Test/"
    _modification = UnityProjectModificationSyncAndroid(
        _testProjectFolder + "Android_modification/",
        _testProjectFolder + "Android_final/",
    )
