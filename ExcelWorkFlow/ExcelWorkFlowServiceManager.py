#!/usr/bin/env python3

from base.supports.Service.ServiceManager import ServiceManager


class ExcelWorkFlowServiceManager(ServiceManager):
    def __init__(self, app_):
        super().__init__(app_)

    def create(self):
        super(ExcelWorkFlowServiceManager, self).create()

    def destory(self):
        super(ExcelWorkFlowServiceManager, self).destory()
