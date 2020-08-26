#!/usr/bin/env python3
from base.supports.App.AppState import AppState
import os


class CocosCreatorAppState(AppState):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(CocosCreatorAppState, self).create()

    def destory(self):
        super(CocosCreatorAppState, self).destory()

    def initAppState(self):
        # meta 数据结构解析
        self.appStateDict["MetaAnalyse"] = ["MetaAnalyse"]
        # 项目构建
        self.appStateDict["Build"] = ["Build"]
        # Prefab 结构解析
        self.appStateDict["PrefabAnalyse"] = ["PrefabAnalyse"]
        # 代码解析
        self.appStateDict["CodeAnalyse"] = ["CodeAnalyse"]

