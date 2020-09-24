#!/usr/bin/env python3
from base.supports.App.App import App
from utils import pyUtils


class CocosCreatorApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        return

    def testStart(self):
        self.start()
        # # 解析 meta
        # self.changeAppState("MetaAnalyse")

        # # 构建
        # self.changeAppState("Build")

        # 解析 prefab
        self.changeAppState("PrefabAnalyse")

        # # 代码解析
        # self.changeAppState("CodeAnalyse")
