#!/usr/bin/env python3
from base.supports.App.AppState import AppState
import os


class ExcelWorkFlowAppState(AppState):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(ExcelWorkFlowAppState, self).create()

    def destory(self):
        super(ExcelWorkFlowAppState, self).destory()

    def initAppState(self):
        # proto 数据结构解析
        self.appStateDict["ProtoStructAnalyse"] = ["ProtoStructAnalyse"]
        self.appStateDict["SwiftCodeAnalyse"] = ["SwiftCodeAnalyse"]
        self.appStateDict["CocosCreatorCodeAnalyse"] = ["CocosCreatorCodeAnalyse"]
        self.appStateDict["SplitTxt"] = ["SplitTxt"]
        self.appStateDict["Proto"] = ["Proto"]
        self.appStateDict["PSDAnalyse"] = ["PSDAnalyse"]
        self.appStateDict["CopyFiles"] = ["CopyFiles"]
