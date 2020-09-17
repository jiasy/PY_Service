import ftplib
import os
from utils import sysUtils


# 获取FTP链接
# _ftpSync = ftpUtils.getFTPSync(地址,用户名,密码,路径<不填的话就是根目录>)
def getFTPSync(host_: str, username_: str, password_: str, ftpFolder_: str = None):
    _ftpSync = FTPSync(host_, username_, password_, ftpFolder_)  # 实例化FTP对象
    return _ftpSync


# 上传目录
def uploadFolder(
        ftpSync_,  # ftpSync 对象
        localFolderPath_,  # 本地的文件夹路径
        ftpFolderPath_=None  # ftp对应文件夹中的子文件夹
):
    _ftpConnect = ftpSync_.ftpConnect

    localFolderPath_ = sysUtils.folderPathFixEnd(localFolderPath_)  # 确保文件夹格式
    _fileList = os.listdir(localFolderPath_)  # 文件夹中的文件列表
    _lastFolder = os.path.abspath('.')  # 先记住之前在哪个工作目录中
    os.chdir(localFolderPath_)  # 然后切换到目标工作目录

    if ftpFolderPath_:
        _currentTargetFolderPath = _ftpConnect.pwd()
        try:
            _ftpConnect.mkd(ftpFolderPath_)
        except Exception:
            pass
        finally:
            _ftpConnect.cwd(os.path.join(_currentTargetFolderPath, ftpFolderPath_))

    for _fileName in _fileList:
        _currentTargetFolderPath = _ftpConnect.pwd()
        _currentLocal = localFolderPath_ + r'/{}'.format(_fileName)
        if os.path.isfile(_currentLocal):
            uploadFile(ftpSync_, localFolderPath_, _fileName, None)
        elif os.path.isdir(_currentLocal):
            try:
                _ftpConnect.mkd(_fileName)
            except:
                pass
            _ftpConnect.cwd("%s/%s" % (_currentTargetFolderPath, _fileName))
            uploadFolder(ftpSync_, _currentLocal)

        # 之前路径可能已经变更，需要再回复到之前的路径里
        _ftpConnect.cwd(_currentTargetFolderPath)

    os.chdir(_lastFolder)


def uploadFile(ftpSync_, localFolderPath_, fileName_, callback_=None):
    _ftpConnect = ftpSync_.ftpConnect
    # 记录当前 ftp 路径
    _currentFolder = _ftpConnect.pwd()

    print("    %s/%s" % (localFolderPath_, fileName_))
    file = open(os.path.join(localFolderPath_, fileName_), 'rb')  # file to send

    _ftpConnect.storbinary('STOR %s' % fileName_, file, callback=callback_)  # send the file
    file.close()  # close file
    _ftpConnect.cwd(_currentFolder)


# 获取当前默认路径下的内容
# ftpUtils.getFileOrFolderList(_ftpSync.ftpConnect)
def getFileOrFolderList(ftpConnect_):
    return ftpConnect_.nlst()


# 遍历FTP上的所有内容，并显示
# _ftpSync.showResOnFtp(_ftpSync)
def showResOnFtp(ftpSync_):
    _ftpFileList = ftpSync_.walk(".")
    for _i in range(len(_ftpFileList)):
        print('_ftpFileList[' + str(_i) + '] = ' + str(_ftpFileList[_i]))
    return _ftpFileList


class FTPSync(object):
    def __init__(self, host_: str, username_: str, password_: str, ftpFolder_: str = None):
        self.ftpConnect = ftplib.FTP(host_, username_, password_)  # host, user, passwd
        self.ftpFolder = ""
        if ftpFolder_:
            # 去掉文件路径后面的 /
            while ftpFolder_[-1] == "/" or ftpFolder_[-1] == "\\":
                ftpFolder_ = ftpFolder_[:-1]
            self.ftpFolder = ftpFolder_
            self.ftpConnect.cwd(self.ftpFolder)  # 远端FTP目录

    def get_dirs_files(self):
        u''' 得到当前目录和文件, 放入dir_res列表 '''
        dir_res = []
        self.ftpConnect.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
        return files, dirs

    # 遍历文件夹
    # ftpUtils.walk('.')
    def walk(self, next_dir, resultList_: list = None):
        # 文件列表
        _resultList = resultList_ if resultList_ else []
        # ftp 端切换到文件夹
        self.ftpConnect.cwd(next_dir)
        # ftp 端的文件夹
        ftp_curr_dir = self.ftpConnect.pwd()
        ftp_relative_curr_dir = ftp_curr_dir.split(self.ftpFolder)[1]
        # ftp 当前指向目录下的文件
        files, dirs = self.get_dirs_files()
        # ftp 端的文件相对路径
        for _file in files:
            _filePath = ftp_relative_curr_dir + "/" + _file
            _resultList.append(_filePath)
            print('_filePath = ' + str(_filePath))
        # 遍历文件夹
        for d in dirs:
            self.ftpConnect.cwd(ftp_curr_dir)  # 切换ftp的当前工作目录为d的父文件夹
            self.walk(d, _resultList)  # 在这个递归里面，本地和ftp的当前工作目录都会被更改
        # 返回结果集
        return _resultList

    # ftp.syncToLocal('.')
    def syncToLocal(self, next_dir):
        # ftp 端切换到文件夹
        self.ftpConnect.cwd(next_dir)
        # 本地创建相同的目录
        try:
            os.mkdir(next_dir)
        except OSError:
            pass
        os.chdir(next_dir)
        # ftp 端的文件夹
        ftp_curr_dir = self.ftpConnect.pwd()
        # 本机的文件夹
        local_curr_dir = os.getcwd()
        # ftp 当前指向目录下的文件
        files, dirs = self.get_dirs_files()
        # 遍历文件
        for f in files:
            print('download :', os.path.abspath(f))
            outf = open(f, 'wb')
            try:
                self.ftpConnect.retrbinary('RETR %s' % f, outf.write)
            finally:
                outf.close()
        # 遍历文件夹
        for d in dirs:
            os.chdir(local_curr_dir)  # 切换本地的当前工作目录为d的父文件夹
            self.ftpConnect.cwd(ftp_curr_dir)  # 切换ftp的当前工作目录为d的父文件夹
            self.syncToLocal(d)  # 在这个递归里面，本地和ftp的当前工作目录都会被更改
