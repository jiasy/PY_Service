#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
import oss2
import os


class OSS(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        # 认证信息
        _access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'ACCESS_KEY_ID')
        _access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'ACCESS_KEY_SECRET')
        # 目标位置
        _endpoint = os.getenv('OSS_TEST_ENDPOINT', 'http://oss-cn-beijing.aliyuncs.com')
        self.syFarmBucketName = "Bucket名称"
        # 本地资源文件夹
        self.resPath = "/Volumes/18604037792/develop/ShunYuan/wxGame/build/wechatgame/res/"
        # OSS 上的目标文件夹
        self.targetFolderPath = "farmRemote/res"
        self.bucket = oss2.Bucket(
            oss2.Auth(_access_key_id, _access_key_secret),
            _endpoint,
            bucket_name=self.syFarmBucketName
        )
        self.service = oss2.Service(oss2.Auth(_access_key_id, _access_key_secret), _endpoint)

    def create(self):
        super(OSS, self).create()
        self.showFiles()

    def destory(self):
        super(OSS, self).destory()

    # 显示指定bucket下的内容
    def showFiles(self):
        print("     %s下有如下文件：" % self.syFarmBucketName)
        for i in oss2.ObjectIterator(self.bucket):
            print(i.key)

    def uploadDir(self, folderPath_: str):
        _filePaths = os.listdir(folderPath_)
        for _filePath in _filePaths:
            _path = folderPath_ + '/' + _filePath
            if os.path.isdir(_path):
                self.uploadDir(_path)
            else:
                _remoteFilePath = self.targetFolderPath + _path.split(self.resPath).pop()
                with open(oss2.to_unicode(_path), 'rb') as _file:
                    self.bucket.put_object(_remoteFilePath, _file)
                _meta = self.bucket.get_object_meta(_remoteFilePath)
                if _meta:
                    print(str(_remoteFilePath) + " 上传成功 +")
                else:
                    print(str(_remoteFilePath) + " 上传失败 xXx")
