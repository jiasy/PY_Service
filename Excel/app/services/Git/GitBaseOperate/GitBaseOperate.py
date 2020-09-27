#!/usr/bin/env python3
# Created by jiasy at 2020/9/27
from base.supports.Base.BaseInService import BaseInService
import utils


class GitBaseOperate(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(GitBaseOperate, self).create()

    def destory(self):
        super(GitBaseOperate, self).destory()

# 获取自己对应的资源
# self.tempFile = fileUtils.getPath(self.resPath, self.className + ".suffix")