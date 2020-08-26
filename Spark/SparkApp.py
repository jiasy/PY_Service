#!/usr/bin/env python3
from base.supports.App.App import App
from utils import pyUtils


class SparkApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        # 换到 Presto 上
        self.changeAppState("Presto")


