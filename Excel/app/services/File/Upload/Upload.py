#!/usr/bin/env python3
# Created by jiasy at 2020/9/10
from base.supports.Base.BaseInService import BaseInService
import utils


class Upload(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(Upload, self).create()

    def destory(self):
        super(Upload, self).destory()

# 获取自己对应的资源
# self.tempFile = fileUtils.getPath(self.resPath, self.className + ".suffix")