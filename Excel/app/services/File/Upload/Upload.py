#!/usr/bin/env python3
# Created by jiasy at 2020/9/9
from utils import sysUtils
from utils import ftpUtils
import os
import oss2

from Excel.ExcelBaseInService import ExcelBaseInService


class Upload(ExcelBaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.funcDict = {
            "OSS": {
                "localFolderPath": "本地文件夹",
                "accessKeyId": "AccessKeyId",
                "accessKeySecret": "AccessKeySecret",
                "endPoint": 'EndPoint',
                "bucketName": "Bucket",
                "filters": "上传文件的后缀过滤",
                "remoteFolderPath": "目标路径",
            },
            "FTP": {
                "localFolderPath": "本地文件夹",
                "ftpHost": "?",
                "ftpUserName": "?",
                "ftpPassWord": "?",
                "ftpFolder": '?',  # 一级子目录
                "ftpSubFolder": "?",  # 二级子目录
            },
        }

    def create(self):
        super(Upload, self).create()

    def destory(self):
        super(Upload, self).destory()

    # 当前文件夹 folderPath_
    # 用来裁切相对路径的 resFolderPath_
    # OSS的目标位置 bucket_
    def uploadDirToOSS(self, currentLocalFolderPath_: str, resFolderPath_: str, bucket_, remoteFolderPath_: str,
                       filters_: list):
        _filePaths = os.listdir(currentLocalFolderPath_)
        for _filePath in _filePaths:
            _path = currentLocalFolderPath_ + '/' + _filePath
            if os.path.isdir(_path):
                self.uploadDirToOSS(_path, resFolderPath_, bucket_, remoteFolderPath_, filters_)
            else:
                _haveBoo = False
                for _i in range(len(filters_)):  # 再过滤列表中查找
                    if _filePath.endswith(filters_[_i]):
                        _haveBoo = True  # 有就标示上
                        break
                if not _haveBoo:  # 不在过滤内容中，直接下一个
                    print("    " + str(_path) + " 过滤，未上传")
                    continue
                _remoteFilePath = remoteFolderPath_ + _path.split(resFolderPath_).pop()  # 上传OSS
                with open(oss2.to_unicode(_path), 'rb') as _file:
                    bucket_.put_object(_remoteFilePath, _file)
                _meta = bucket_.get_object_meta(_remoteFilePath)
                if _meta:
                    print("    " + str(_remoteFilePath) + " 上传成功 +")
                else:
                    print("    " + str(_remoteFilePath) + " 上传失败 x")

    def OSS(self, dParameters_: dict):
        _localFilePath = sysUtils.folderPathFixEnd(dParameters_["localFolderPath"])
        _remoteFolderPath = sysUtils.folderPathFixEnd(dParameters_["remoteFolderPath"])
        _bucket = oss2.Bucket(
            oss2.Auth(
                dParameters_["accessKeyId"],
                dParameters_["accessKeySecret"]
            ),
            dParameters_["endPoint"],
            bucket_name=dParameters_["bucketName"]
        )
        self.uploadDirToOSS(
            _localFilePath,
            _localFilePath,
            _bucket,
            _remoteFolderPath,
            dParameters_["filters"]
        )

    def FTP(self, dParameters_: dict):
        _localFilePath = sysUtils.folderPathFixEnd(dParameters_["localFolderPath"])
        _ftpSync = ftpUtils.getFTPSync(
            dParameters_["ftpHost"],
            dParameters_["ftpUserName"],
            dParameters_["ftpPassWord"],
            dParameters_["ftpFolder"]
        )
        ftpUtils.uploadFolder(
            _ftpSync,
            _localFilePath,
            dParameters_["ftpSubFolder"]
        )


import Main

if __name__ == "__main__":
    # 直接复制，到新文件中，只需要改，所需参数 和 命令行参数
    _folderPath = os.path.dirname(os.path.realpath(__file__))  # 当前执行目录
    _folderSplit = os.path.split(_folderPath)  # 切目录
    _baseServiceName = os.path.split(_folderSplit[0])[1]  # 再切得到上一层文件夹名
    _subBaseInServiceName = _folderSplit[1]  # 切到的后面就是子服务名称

    # _functionName = "OSS"
    # _parameterDict = {  # 所需参数
    #     "localFolderPath": "{resFolderPath}",
    #     "accessKeyId": "?",
    #     "accessKeySecret": "?",
    #     "endPoint": '?',
    #     "bucketName": "?",
    #     "filters": [
    #         ".txt"
    #     ],
    #     "remoteFolderPath": "farmRemote/test",
    # }

    _functionName = "FTP"
    _parameterDict = {  # 所需参数
        "localFolderPath": "{resFolderPath}",
        "ftpHost": "?",
        "ftpUserName": "?",
        "ftpPassWord": "?",
        "ftpFolder": '?',  # 一级子目录
        "ftpSubFolder": "?",  # 二级子目录
    }

    Main.excelProcessStepTest(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        _parameterDict,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )

    Main.execExcelCommand(
        _baseServiceName,
        _subBaseInServiceName,
        _functionName,
        {  # 命令行参数
            "executeType": "单体测试"
        }
    )
