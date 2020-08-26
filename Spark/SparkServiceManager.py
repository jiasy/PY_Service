#!/usr/bin/env python3

from base.supports.Service.ServiceManager import ServiceManager
import os


class SparkServiceManager(ServiceManager):
    def __init__(self, app_):
        super().__init__(app_)

    def create(self):
        super(SparkServiceManager, self).create()

    def destory(self):
        super(SparkServiceManager, self).destory()
