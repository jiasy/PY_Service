#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *


class Proto(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(Proto, self).create()
        self.getSubClassObject("PbCreator")

        fileCopyUtils.copyFilesInFolderTo(
            [".proto"],
            "/Volumes/18604037792/develop/ShunYuan/protocol_farm/server/",
            "/Volumes/18604037792/develop/ShunYuan/openresty/proto/",
            "include",
            True
        )

        # 通过命令行驱动pb文件生成
        self.pbCreator.createPbFile(
            "/Volumes/18604037792/develop/ShunYuan/openresty/proto/",
            "/Volumes/18604037792/develop/ShunYuan/openresty/app/lua/protobuf/pb/"
        )

    def destory(self):
        super(Proto, self).destory()
