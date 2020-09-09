#!/usr/bin/env python3
from base.supports.App.AppState import AppState
import os


class ExcelAppState(AppState):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(ExcelAppState, self).create()

    def destory(self):
        super(ExcelAppState, self).destory()

    def initAppState(self):
        # 服务是动态添加卸载的，不用设置服务状态配置
        return
