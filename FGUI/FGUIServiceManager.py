#!/usr/bin/env python3

from base.supports.Service.ServiceManager import ServiceManager
import os


class FGUIServiceManager(ServiceManager):
    def __init__(self, app_):
        super().__init__(app_)

    def create(self):
        super(FGUIServiceManager, self).create()

    def destory(self):
        super(FGUIServiceManager, self).destory()
