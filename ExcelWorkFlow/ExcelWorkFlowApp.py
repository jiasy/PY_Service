#!/usr/bin/env python3
from base.supports.App.App import App
from utils import listUtils


class ExcelWorkFlowApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        return

    def testStart(self):
        self.start()

        # self.ProtoStructAnalyse()  # 解析Proto
        # self.FileOperate()  # 文件操作
        self.CopyFiles()  # 拷贝文件夹内容

        # self.changeAppState("SwiftCodeAnalyse")
        # self.changeAppState("CocosCreatorCodeAnalyse") # 解析 CocosCreator的结构
        # self.changeAppState("SplitTxt")  # 切割小说文本
        # self.changeAppState("Proto")  # Proto相关工具
        # self.changeAppState("PSDAnalyse")  # PSD 工具

        return

    def ProtoStructAnalyse(self):
        _service = self.getSingleRunningService("ProtoStructAnalyse")
        _tableStructureStrList = _service.analyseProtoStructureInFolder(
            # "/Volumes/Files/develop/GitHub/PY_Service/Excel/res/services/Proto/ProtoConvert/proto/"
            "/Volumes/18604037792/develop/ShunYuan/protocol_farm/server/"
        )
        listUtils.printList(_tableStructureStrList)

    def FileOperate(self):
        _service = self.getSingleRunningService("FileOperate")
        # _service.removeFirstCharsInEveryLine("/Users/jiasy/Desktop/BuildAndroid_Fail", 9)
        # _service.removeFirstCharsInEveryLine("/Users/jiasy/Desktop/BuildAndroid_Success", 9)
        # _service.removeFirstCharsInEveryLine("/Users/jiasy/Desktop/BuildIOS", 9)

    def CopyFiles(self):
        _service = self.getSingleRunningService("CopyFiles")
        _service.coverFiles(
            [".json"],  # 拷贝那些类型
            "/Volumes/18604037792/develop/ShunYuan/farm/genXml/json/",  # 从哪里拷贝
            "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/resources/Json/",  # 拷贝去哪里
            True
        )
