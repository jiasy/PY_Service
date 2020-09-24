#!/usr/bin/env python3
from base.supports.App.App import App


class TestApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        return

    def testStart(self):
        self.start()
        # 测试框架支持
        self.changeAppState("PYService")
