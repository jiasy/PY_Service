#!/usr/bin/env python3
from base.supports.App.App import App
from utils import pyUtils


class ExcelWorkFlowApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        self.changeAppState("ProtoStructAnalyse") # 解析 Proto结构，生成SQL
        # self.changeAppState("SwiftCodeAnalyse")
        # self.changeAppState("CocosCreatorCodeAnalyse") # 解析 CocosCreator的结构
        # self.changeAppState("SplitTxt")  # 切割小说文本
        # self.changeAppState("Proto")  # Proto相关工具
        # self.changeAppState("CopyFiles")  # 拷贝文件夹内容
        # self.changeAppState("PSDAnalyse")  # PSD 工具
