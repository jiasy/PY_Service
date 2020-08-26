# !/usr/bin/env python3

import pyhdfs
from pyhdfs import HdfsClient
import utils.listUtils


# 显示文件夹结构
def showAllDirAndFiles(client_: HdfsClient, path_: str):
    for _root, _dir, _files in client_.walk(path_, status=True):
        print('_root = ' + str(_root))
        print('_dir = ' + str(_dir))
        print('_files = ' + str(_files))


# 显示文件夹结构
def showDirs(client_: HdfsClient, path_: str, maxDepth_: int, list_: list, depth_: int = 0):
    if depth_ > maxDepth_:
        return
    for _sub in client_.listdir(path_):
        _filePath = path_ + _sub
        _fileStatus = client_.get_file_status(_filePath)
        # print('_fileStatus = ' + str(_fileStatus))
        if _fileStatus.type == "DIRECTORY":
            if _fileStatus.permission == '711':
                print("|      " * depth_ + "+--" + _sub + "     permission is 711")
            elif _fileStatus.permission == '700':
                print("|      " * depth_ + "+--" + _sub + "     permission is 700")
            elif _fileStatus.permission == '733':
                print("|      " * depth_ + "+--" + _sub + "     permission is 733")
            elif _fileStatus.permission == '770':
                print("|      " * depth_ + "+--" + _sub + "     permission is 770")
            else:
                print("|      " * depth_ + "+--" + _sub)
                list_.append(_filePath)
                showDirs(client_, _filePath + '/', maxDepth_, list_, depth_ + 1)


'''
pyhdfs
1. 建立连接，创建一个客户端
    client = pyhdfs.HdfsClient(hosts="45.91.43.237,9000",user_name="hadoop")
    可用参数
    hosts:主机名 IP地址与port号之间需要用","隔开 如:hosts="45.91.43.237,9000" 多个主机时可以传入list， 如:["47.95.45.254,9000","47.95.45.235,9000"]
    randomize_hosts：随机选择host进行连接，默认为True
    user_name:连接的Hadoop平台的用户名
    timeout:每个Namenode节点连接等待的秒数，默认20sec
    max_tries:每个Namenode节点尝试连接的次数,默认2次
    retry_delay:在尝试连接一个Namenode节点失败后，尝试连接下一个Namenode的时间间隔，默认5sec
    requests_session:连接HDFS的HTTP request请求使用的session，默认为None
'''
'''
2. 返回这个用户(user_name)持有的根目录 
    client.get_home_directory() -> /user/hadoop
3. 返回可用的namenode节点
    client.get_active_namenode() -> 45.91.43.237:50070
4. 返回指定目录下的所有文件
    client.listdir("/user/hadoop") -> [u'.password', u'.sparkStaging' ...]
5. 打开一个远程节点上的文件，返回一个HTTPResponse对象
    response = client.open("/user/hadoop/speech_text.txt")
    # 查看文件内容
    response.read()
6.从本地上传文件至集群
    copy_from_local(localsrc, dest, **kwargs)
7.从集群上copy到本地
    copy_to_local(src, localdest, **kwargs)
        # 从本地上传文件至集群之前，集群的目录
        print "Before copy_from_local"
        print client.listdir("/user/hadoop")
         
        # 从本地上传文件至集群
        client.copy_from_local("D:/Jupyter notebook/ipynb_materials/src/test.csv","/user/hadoop/test.csv")
         
        # 从本地上传文件至集群之后，集群的目录
        print "After copy_from_local"
        print client.listdir("/user/hadoop")
    
8.向一个已经存在的文件中插入文本
    append(path, data, **kwargs)
        # 使用append函数插入string
        client.append("/user/hadoop/test.csv","0,2,0\r\r\n")
        # 再看看文件中的内容
        response = client.open("/user/hadoop/test.csv")
        response.read()

9.融合两个文件
    concat(target, sources, **kwargs)
    
10.创建新目录
    mkdirs(path, **kwargs)
        client.mkdirs("/user/hadoop/data")
        # 再看看当前路径下的文件
        # 多了个data路径
        client.listdir("/user/hadoop/")
11.查看是否存在文件
    exists(path, **kwargs)
        # 查看文件是否存在
        client.exists("/user/hadoop/test.csv")
        
12.查看路径总览信息
    get_content_summary(path, **kwargs)
        # 查看路径总览信息
        client.get_content_summary("/user/hadoop")
        
13.查看文件的校验和(checksum)
    get_file_checksum(path, **kwargs)
        # 查看文件的校验和(checksum)
        client.get_file_checksum("/user/hadoop/test.csv")
14.查看当前路径的状态(可路径可文件)
    list_status(path, **kwargs)
        # 查看当前路径下的文件状态
        client.list_status("/user/hadoop")
'''


def getClient(url_: str, userName_: str):
    if userName_:
        return pyhdfs.HdfsClient(hosts=url_, user_name=userName_)
    else:
        return pyhdfs.HdfsClient(hosts=url_)



# 获取文件夹内有文件的文件夹路径。这样的路径都是有数据
def getAllFolderHaveData(client_: HdfsClient, path_: str):
    _folderPathList = []
    for _root, _dir, _files in client_.walk(path_, status=True):
        # 有文件的内容的文件夹才是需要拷贝的文件夹
        if len(_files) > 0:
            print(_root)
            _folderPathList.append(_root)
    return utils.listUtils.joinListToStr(_folderPathList, "\n")


if __name__ == "__main__":
    _client = getClient("hadoop-1.loho.local", "hadoop")
    # _client = getClient("139.224.8.82", "hadoop")
    _homeDir = _client.get_home_directory()
    print('_homeDir = ' + str(_homeDir))
    _activeNode = _client.get_active_namenode()
    print('_activeNode = ' + str(_activeNode))
    # _client.copy_from_local("/Users/jiasy/Desktop/MeiQia", "/ods/thirdPparty/MeiQia", overwrite=True)
    _filePathList = []
    showDirs(_client, "/drp/hive_external/", 2, _filePathList)
    print('_filePathList = ' + str(_filePathList))
