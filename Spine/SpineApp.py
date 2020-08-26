#!/usr/bin/env python3
from base.supports.App.App import App
from utils import pyUtils


class SpineApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        self.changeAppState("SpineAnalyse")  # 解析 Spine 导出的东西
