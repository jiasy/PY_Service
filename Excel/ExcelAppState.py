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
        return
