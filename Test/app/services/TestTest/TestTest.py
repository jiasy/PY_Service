#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
import os
from utils import pyUtils


class TestTest(BaseService):

    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(TestTest, self).create()
        self.test_matplotlib()

    def destory(self):
        super(TestTest, self).destory()

    def test_matplotlib(self):
        _matplotlib = self.getSubClassObject("Matplotlib")
        _matplotlib.doTest()


