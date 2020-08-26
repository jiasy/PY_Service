#!/usr/bin/env python3

from base.supports.Service.ServiceManager import ServiceManager


class MathServiceManager(ServiceManager):

    def __init__(self, app_):
        super().__init__(app_)

    def create(self):
        super(MathServiceManager, self).create()

    def destory(self):
        super(MathServiceManager, self).destory()
