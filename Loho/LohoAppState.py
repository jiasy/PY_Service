#!/usr/bin/env python3
from base.supports.App.AppState import AppState
import os


class LohoAppState(AppState):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(LohoAppState, self).create()

    def destory(self):
        super(LohoAppState, self).destory()

    def initAppState(self):
        self.appStateDict["SqlMaker"] = ["SqlMaker"]
        self.appStateDict["LohoTest"] = ["LohoTest"]
