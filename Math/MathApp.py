#!/usr/bin/env python3
from base.supports.App.App import App
from utils import pyUtils


class MathApp(App):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    def start(self):
        return

    def testStart(self):
        self.start()
        # LinearAlgebra 线性代数，模块
        # self.changeAppState("LinearAlgebra")
        # NumPy 模块
        self.changeAppState("NumPy")


