#!/usr/bin/env python3
from base.supports.App.App import App
from utils import pyUtils


class UnityApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        return

    def testStart(self):
        self.start()
        # self.changeAppState("UnityAnalyse")
        self.changeAppState("UnityCSharpAnalyse")  # 解析 C#
        # self.changeAppState("UnityLuaAnalyse")  # 解析 Lua
