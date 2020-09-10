#!/usr/bin/env python3
# Created by jiasy at 2019/1/29
from base.supports.Base.BaseInService import BaseInService
from utils import fileUtils


class OLAP_chuanqi_D(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.sqlFilePath = fileUtils.getPath(self.subResPath, self.className + ".sql")

    def create(self):
        super(OLAP_chuanqi_D, self).create()

    def destory(self):
        super(OLAP_chuanqi_D, self).destory()
