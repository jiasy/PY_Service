#!/usr/bin/env python3
from base.supports.App.AppState import AppState
import os


class SparkAppState(AppState):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SparkAppState, self).create()

    def destory(self):
        super(SparkAppState, self).destory()

    def initAppState(self):
        self.appStateDict["Presto"] = ["Presto"]
