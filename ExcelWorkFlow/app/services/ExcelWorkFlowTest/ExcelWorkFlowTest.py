#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
import os
from utils import pyUtils


# Excel 驱动 工作流
class ExcelWorkFlowTest(BaseService):

    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        self.sm.test = self
        super(ExcelWorkFlowTest, self).create()

    def destory(self):
        super(ExcelWorkFlowTest, self).destory()
        self.sm.test = None
