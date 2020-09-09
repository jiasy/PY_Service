#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import folderUtils
from utils import fileUtils
from utils import cmdUtils
from utils import listUtils
import sys


class SpineExport(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SpineExport, self).create()
        self.spineAppPath = "/Applications/Spine/Spine.app/Contents/MacOS/Spine"

        # Spine 的骨骼和皮肤是分开的，在运行时组装，这样可以多个骨骼使用同一套图片。
        self.exportSpineInFolder(
            # -------------- 骨骼信息
            "/Volumes/18604037792/develop/ShunYuan/SPINE/source/",  # 内容导出到目标文件夹
            "/Volumes/18604037792/develop/ShunYuan/SPINE/output/",  # 动画文件的目标文件夹
            "/Volumes/18604037792/develop/ShunYuan/SPINE/export.json",  # spine编辑器，导出选项中，保存出来的导出配置
            # -------------- 皮肤信息
            "/Volumes/18604037792/develop/ShunYuan/SPINE/source/imgs/",  # 图片
            "/Volumes/18604037792/develop/ShunYuan/SPINE/output/",  # altas 导出文件夹
            "/Volumes/18604037792/develop/ShunYuan/SPINE/pack.json",  # spine编辑器，纹理打包，保存出来的打包配置
            "PyramidSheet"  # altas 的前缀
        )

    def destory(self):
        super(SpineExport, self).destory()

    def exportSpineInFolder(self,
                            spineFolderPath_: str, jsonOutputFolderPath_: str, exportJsonPath_: str,
                            pngFolderPath_: str, altasOutputFolderPath_: str, packJsonPath_: str, altasName_: str
                            ):
        folderUtils.makeSureDirIsExists(jsonOutputFolderPath_)
        _spineList = folderUtils.getFilterFilesInPath(spineFolderPath_, [".spine"])
        # spine 名称队列，用于校验导出骨骼信息是否匹配
        _spineJustNameList = []
        # 根据配置，导出动画文件
        _cmd = self.spineAppPath
        for _i in range(len(_spineList)):
            _spinePath = _spineList[_i]
            _spineJustNameList.append(fileUtils.justName(_spinePath))
            _cmd = _cmd + " -i " + _spinePath + " -m -o " + jsonOutputFolderPath_ + " -e " + exportJsonPath_ + " "
        _pipeLines = cmdUtils.doStrAsCmd(_cmd, spineFolderPath_, False)
        if not _pipeLines:
            sys.exit(1)
        # 发布动画是否和文件名一致，导出的文件是按照动画编辑时的骨骼命名进行的，有可能骨骼和文件的名称不一致，需要提示。
        _outputJsonPathList = folderUtils.getFilterFilesInPath(jsonOutputFolderPath_, [".json"])
        for _i in range(len(_outputJsonPathList)):
            _outputJsonPath = _outputJsonPathList[_i]
            listUtils.findAndRemove(_spineJustNameList, fileUtils.justName(_outputJsonPath))
        if len(_spineJustNameList) > 0:
            print("spine骨骼与Spine文件名不一致")
            for _i in range(len(_spineJustNameList)):
                print("    " + _spineJustNameList[_i])
            sys.exit(1)

        # 根据配置，打包图片
        _cmd = self.spineAppPath
        _cmd = _cmd + " -i " + pngFolderPath_ + " -o " + altasOutputFolderPath_ + " -n " + altasName_ + " -p " + packJsonPath_
        _pipeLines = cmdUtils.doStrAsCmd(_cmd, spineFolderPath_, False)
        if not _pipeLines:
            sys.exit(1)


'''
Spine Launcher 3.8.97
Esoteric Software Llc (C) 2013-2020 | Http://Esotericsoftware.Com

Usage:
  Editor: Spine [-Hfkltv] [-X <Host:Port>] [-U <Version>] [<Path>]
  Export: Spine [-I <Path>] [-M] [-O <Path>] -E <Path>
  Import: Spine -I <Path> [-S <Scale>] -O <Path> -R [<Name>]
Clean Up: Spine -I <Path> -M
    Pack: Spine -I <Path> [-J <Path>]... -O <Path> -P <Name>
          Spine -I <Path> [-J <Path>]... -O <Path> [-N <Name>] -P <Path>
    Info: Spine -I <Path>

Editor:
-H, --Help       Print This Help Message And Exit.
-F, --Force      Force Download Of The Spine Update.
-K, --Keys       Enable Hotkey Popups By Default.
-L, --Logout     Logout, Removing Activation Code.
-T, --Notimeout  Disable Timeout When Checking For And Downloading Updates.
-V, --Version    Print Version Information And Exit.
-X, --Proxy      Proxy Server To Use When Checking For And Downloading Updates.
-U, --Update     The Version Number Of The Spine Update To Load.
Project.Spine    Path To A Spine Project File To Open.

Export Json, Binary, Images, Or Video:
-I, --Input   Path To A Folder, Project, Or Data File. Overrides Export Json.
-M, --Clean   Animation Clean Up Is Performed Before Export.
-O, --Output  Path To Write Export File(S). Overrides Export Json.
-E, --Export  Path To Export Settings Json File.

Import Json, Binary, Or A Project's Skeletons Into Another Project:
-I, --Input   Path To A Folder, Project, Or Data File To Be Imported.
-O, --Output  Path To Project File To Import Into. Created If Nonexistent.
-S, --Scale   Scale The Project Being Imported.
-R, --Import  Perform A Skeleton Import. The Skeleton Name May Be Omitted.

Animation Clean Up:
-I, --Input   Path To Project File Or Folder.
-M, --Clean   Animation Clean Up Is Performed And The Project Is Saved.

Texture Atlas Packing:
-I, --Input   Path To Folder Of Images To Be Packed.
-O, --Output  Path To Write Texture Atlas And Png Files.
-J, --Project Path To A Project To Determine Which Images Are Used By Meshes.
-N, --Name    Texture Atlas Name, The Prefix For The Atlas And Png Files.
-P, --Pack    Texture Atlas Name Or Path To Pack Settings Json File.

Texture Atlas Unpacking:
-I, --Input   Path To Folder Of Atlas Images.
-O, --Output  Path To Write Unpacked Image Files.
-C, --Unpack  Path To Texture Atlas File.

Project Information:
-I, --Input   Path To Project Or Data File.

Examples:
Spine --Export /Path/To/Export.Json
Spine --Export "/Path/With Spaces/To/Export.Json"
Spine --Input /Path/To/Project.Spine --Output /Path/To/Output/
      --Export /Path/To/Export.Json
Spine -I /Path/To/Project.Spine -O /Path/To/Output/ -E /Path/To/Export.Json
Spine -E /Path/To/Export1.Json -E /Path/To/Export2.Json
Spine -I /Path/To/Images/ -O /Path/To/Output/ --Pack /Path/To/Pack.Json
Spine -I /Path/To/Images/ -O /Path/To/Output/ -N Name -P /Path/To/Pack.Json
Spine -I /Path/To/Project1.Spine -O /Path/To/Output/ -E /Path/To/Export1.Json
      -I /Path/To/Project2.Spine -E /Path/To/Export2.Json -I /Path/To/Images/
      -O /Path/To/Output/ -P /Path/To/Pack.Json
Spine -I /Path/To/Skeleton.Json -O /Path/To/Project.Spine -R Skeletonname
'''
