#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService

import os


class EventCenter(BaseService):


    def __init__(self, sm_):
        super().__init__(sm_)
        self.sm.ec = self

    def create(self):
        self.sm.ec = self
        super(EventCenter, self).create()

    def destory(self):
        super(EventCenter, self).destory()
        self.sm.ec = None
