# !/usr/bin/env python3
import os
import shutil
import subprocess


# 前置工作
# Unity 构建一次 Xcode Project。为 modificationFolder
# 复制 modificationFolder。在工程中删除 Classes 和 Library，选移除到废纸篓。再保持Data文件夹，删除其中的内容。为 sourceProjectFolder
# 使用工具对比 sourceProjectFolder -> modificationFolder 的变化并保留，生成 ModificationJson
# Unity 走正常的构建流程，生成已经接入SDK的工程，仿造1.处理掉 Classes、Library、Data文件夹，构成 Unity 的 Xcode Project 壳子。为 templateProjectFolder
# 复制 templateProjectFolder 并在其基础上，应用 ModificationJson 记录的变化，制作成 finalProjectFolder

class UnityProjectModificationSync(object):
    def __init__(self,
                 modificationToolPath_: str,  # 工程修改器路径
                 sourceProjectFolder_: str,  # 修改前
                 modificationFolder_: str,  # 修改后
                 modificationJsonFolder_: str,  # 修改前后配置JSON生成到哪里
                 templateProjectFolder_: str,  # 将配置引用给谁
                 finalProjectFolder_: str  # 谁复制到哪里后，在应用修改
                 ):
        print("1 - compare projects : ")
        # 对比变更
        _modificationJsonPath = self.getModificationJson(
            modificationToolPath_,
            sourceProjectFolder_,
            modificationFolder_,
            modificationJsonFolder_
        )
        print("    diff json : " + _modificationJsonPath)

        # 重新生成最终工程
        print("2 - create new finalProjectFolder : ")
        if os.path.exists(finalProjectFolder_):
            print("    remove : " + finalProjectFolder_)
            shutil.rmtree(finalProjectFolder_, ignore_errors=True)
        print("    copy : " + templateProjectFolder_ + " -> " + finalProjectFolder_)
        shutil.copytree(templateProjectFolder_, finalProjectFolder_)

        # 将 Class、Libraries、Data 拷贝到 最终文件夹
        print("3 - operate finalProjectFolder : ")
        print("    reset Classes")
        if os.path.exists(finalProjectFolder_ + "/Classes"):
            shutil.rmtree(finalProjectFolder_ + "/Classes")
        shutil.copytree(modificationFolder_ + "/Classes", finalProjectFolder_ + "/Classes")

        print("    reset Libraries")
        if os.path.exists(finalProjectFolder_ + "/Libraries"):
            shutil.rmtree(finalProjectFolder_ + "/Libraries")
        shutil.copytree(modificationFolder_ + "/Libraries", finalProjectFolder_ + "/Libraries")

        print("    reset Data")
        if os.path.exists(finalProjectFolder_ + "/Data"):
            shutil.rmtree(finalProjectFolder_ + "/Data")
        shutil.copytree(modificationFolder_ + "/Data", finalProjectFolder_ + "/Data")

        print("4 - modificate finalProjectFolder : ")
        # 将对比引用于最终工程
        self.applyModificationJson(
            modificationToolPath_,
            finalProjectFolder_,
            modificationJsonFolder_,
            _modificationJsonPath
        )
        print("5 - SUCCESS")
        print("    --------------------")
        print("6 - DIY Step")
        # Libraries 中 Plugins 还有 ThridParty 要再贴回去
        print("    reset Libraries/Plugins")
        shutil.copytree(templateProjectFolder_ + "/Libraries/Plugins", finalProjectFolder_ + "/Libraries/Plugins")
        print("    reset Libraries/ThridParty")
        shutil.copytree(templateProjectFolder_ + "/Libraries/ThridParty", finalProjectFolder_ + "/Libraries/ThridParty")

    def getModificationJson(self,
                            modificationToolPath_: str,
                            sourceProjectFolder_: str,
                            modificationFolder_: str,
                            modificationJsonFolder_: str
                            ):

        _cmdStr = modificationToolPath_ + " -compare " + modificationFolder_ + "Unity-iPhone.xcodeproj/project.pbxproj -o " + modificationJsonFolder_ + " " + sourceProjectFolder_ + "Unity-iPhone.xcodeproj/project.pbxproj"
        print("    " + _cmdStr)
        subprocess.Popen(
            _cmdStr,
            shell=True,
            cwd=modificationJsonFolder_,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        _modificationJsonPath = modificationJsonFolder_ + "/JsonConfiguration.json"
        return _modificationJsonPath

    def applyModificationJson(self,
                              modificationToolPath_: str,
                              finalProjectFolder_: str,
                              modificationJsonFolder_: str,
                              modificationJsonPath_: str
                              ):
        _cmdStr = modificationToolPath_ + " -apply " + modificationJsonPath_ + " " + finalProjectFolder_ + "Unity-iPhone.xcodeproj/project.pbxproj"
        print("    " + _cmdStr)
        subprocess.Popen(
            _cmdStr,
            shell=True,
            cwd=modificationJsonFolder_,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )


if __name__ == "__main__":
    _testProjectFolder = "/Volumes/18604037792/develop/ShunYuan/tolua_Build_Project/IOS_Test/"
    _modification = UnityProjectModificationSync(
        "/Volumes/Files/XCodeCache/DerivedData/pbxprojHelper-cymkoramvixxwvfmzoczqihvqpkr/Build/Products/Debug/pbxproj",
        _testProjectFolder + "IOS_sourceProject/",
        _testProjectFolder + "IOS_modification/",
        _testProjectFolder + "",
        _testProjectFolder + "IOS_templateProject/",
        _testProjectFolder + "IOS_finalProject/",
    )
