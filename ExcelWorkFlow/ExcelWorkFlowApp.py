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
        
        self.ProtoStructAnalyse()  # 解析Proto
        # self.changeAppState("SwiftCodeAnalyse")
        # self.changeAppState("CocosCreatorCodeAnalyse") # 解析 CocosCreator的结构
        # self.changeAppState("SplitTxt")  # 切割小说文本
        # self.changeAppState("Proto")  # Proto相关工具
        # self.changeAppState("CopyFiles")  # 拷贝文件夹内容
        # self.changeAppState("PSDAnalyse")  # PSD 工具

        return

    def ProtoStructAnalyse(self):
        _service = self.getSingleRunningService("ProtoStructAnalyse")
        _tableStructureStrList = _service.analyseProtoStructureInFolder(
            "/Volumes/Files/develop/GitHub/PY_Service/Excel/res/services/Proto/ProtoConvert/proto/"
        )
        listUtils.printList(_tableStructureStrList)
