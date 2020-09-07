#!/usr/bin/env python3

from base.supports.Service.ServiceManager import ServiceManager


class ExcelServiceManager(ServiceManager):
    def __init__(self, app_):
        super().__init__(app_)

    def create(self):
        super(ExcelServiceManager, self).create()

    def destory(self):
        super(ExcelServiceManager, self).destory()
