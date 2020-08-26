# !/usr/bin/env python3

import os, pickle, gzip


def save_object_to_zip(objects, filename):
    if not os.path.exists(filename):
        file_path = os.path.split(filename)[0]
        if file_path and not os.path.exists(file_path):  # 需要文件夹
            os.mkdir(os.path.split(filename)[0])  # 创建文件夹
        os.mknod(filename)  # 创建文件
    fil = gzip.open(filename, 'wb')
    pickle.dump(objects, fil)
    fil.close()


def load_object_from_zip(filename):
    fil = gzip.open(filename, 'rb')
    while True:
        try:
            return pickle.load(fil)
        except EOFError:
            break
    fil.close()


def saveData(appName_, dataName_, data_):
    _fileName = "localStroage_" + appName_ + "_" + dataName_
    save_object_to_zip(data_, _fileName)


def loadData(appName_, dataName_):
    _fileName = "localStroage_" + appName_ + "_" + dataName_
    return load_object_from_zip(_fileName)
