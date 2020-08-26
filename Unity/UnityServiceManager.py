#!/usr/bin/env python3

from base.supports.Service.ServiceManager import ServiceManager


class UnityServiceManager(ServiceManager):
    def __init__(self, app_):
        super().__init__(app_)

    def create(self):
        super(UnityServiceManager, self).create()

    def destory(self):
        super(UnityServiceManager, self).destory()
