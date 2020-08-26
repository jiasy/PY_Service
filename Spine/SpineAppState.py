#!/usr/bin/env python3
from base.supports.App.AppState import AppState
import os


class SpineAppState(AppState):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SpineAppState, self).create()

    def destory(self):
        super(SpineAppState, self).destory()

    def initAppState(self):
        self.appStateDict["SpineAnalyse"] = ["SpineAnalyse"]
