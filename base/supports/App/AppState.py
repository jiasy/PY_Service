#!/usr/bin/env python3
from base.supports.Base.Base import Base
from utils import pyUtils


class AppState(Base):

    def __init__(self, sm_):
        super().__init__(sm_)
        self.appStateDict: dict = {}
        self.appStateDict["test"] = [self.app.appName + "Test"]

    def create(self):
        super(AppState, self).create()
        self.initAppState()

    def destory(self):
        super(AppState, self).destory()

    def initAppState(self):
        self.raiseError(pyUtils.getCurrentRunningFunctionName(), "initAppState is not implemented")
