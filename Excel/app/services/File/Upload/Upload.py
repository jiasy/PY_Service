#!/usr/bin/env python3
# Created by jiasy at 2020/9/9
from utils import sysUtils
from utils import ftpUtils
from utils import folderUtils
from utils import fileUtils
import os
import oss2

from Excel.ExcelBaseInService import ExcelBaseInService
import paramiko


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
                "ftpHost": "ftpHost",
                "ftpUserName": "ftpUserName",
                "ftpPassWord": "ftpPassWord",
                "ftpFolder": 'ftpFolder',  # 一级子目录
                "ftpSubFolder": "ftpSubFolder",  # 二级子目录
            },
            "SFTP": {
                "localFolderPath": "本地放置的要上传的文件",
                "filters": "用来过滤的后缀",
                "upToFolderPath": "上传到哪里",
                "ip": "ip地址",
                "port": "端口",
                "username": "root",
                "pKeyFilePath": "id_rsa 秘钥的本机路径",
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

    def SFTP(self, dParameters_: dict):
        # 本地路径 和 上传路径
        _localFolderPath = sysUtils.folderPathFixEnd(dParameters_["localFolderPath"])
        _upToFolderPath = sysUtils.folderPathFixEnd(dParameters_["upToFolderPath"])

        # 传送对象
        _transport = paramiko.Transport(
            (dParameters_["ip"], int(dParameters_["port"]))  # 这个括号不能拆
        )

        # 链接
        _transport.connect(
            username=dParameters_["username"],
            pkey=paramiko.RSAKey.from_private_key_file(dParameters_["pKeyFilePath"])
        )
        # 创建sftp
        _sftp = paramiko.SFTPClient.from_transport(_transport)

        # 遍历本地路径，获取文件列表
        _filePathList = folderUtils.getFileListInFolder(
            _localFolderPath,
            dParameters_["filters"]
        )
        # 依次发送到FTP
        for _idx in range(len(_filePathList)):
            _filePath = _filePathList[_idx]
            _upToFilePath = fileUtils.getNewNameKeepFolderStructure(
                _localFolderPath, _upToFolderPath, _filePath
            )
            _sftp.put(_filePath, _upToFilePath, confirm=True)
            print(_filePath + " -> " + _upToFilePath)


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

    # _functionName = "FTP"
    # _parameterDict = {  # 所需参数
    #     "localFolderPath": "{resFolderPath}",
    #     "ftpHost": "?",
    #     "ftpUserName": "?",
    #     "ftpPassWord": "?",
    #     "ftpFolder": '?',  # 一级子目录
    #     "ftpSubFolder": "?",  # 二级子目录
    # }

    _functionName = "SFTP"
    _parameterDict = {  # 所需参数
        "localFolderPath": "/Volumes/18604037792/develop/ShunYuan/杂项/icons/",
        "filters": [".png", ".jpg"],
        "upToFolderPath": "/home/www/farm/static/icons/",
        "ip": "111.11.111.11",
        "port": 22,
        "username": "root",
        "pKeyFilePath": "/Volumes/18604037792/develop/ShunYuan/杂项/id_rsa",
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
