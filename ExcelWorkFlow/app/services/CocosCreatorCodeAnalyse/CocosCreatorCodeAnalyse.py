#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import folderUtils
from utils import fileUtils
import re
import os
import shutil


# ________________________________________________________________________________________________________________________________________________________
def addLogFun(startLogCount_: int, endLogCount_: int):
    logCode = '\n'
    logCode += 'var _global = window;' + '\n'
    logCode += 'if(_global["getPropertys"]){' + '\n'
    logCode += '}else{' + '\n'
    logCode += '	_global.getPropertys = function (obj){					' + '\n'
    logCode += '		var argumertsStr="";				' + '\n'
    logCode += '		argumertsStr="  | ";				' + '\n'
    logCode += '		for (var key in obj) {				' + '\n'
    logCode += '			if (obj.hasOwnProperty(key)) {			' + '\n'
    logCode += '				var element = obj[key];		' + '\n'
    logCode += '				if (typeof element =="string"){		' + '\n'
    logCode += '					argumertsStr+= key +" : "+element;	' + '\n'
    logCode += '				}else if(typeof element =="number"){		' + '\n'
    logCode += '					argumertsStr+= key +" : "+element.toFixed(2);	' + '\n'
    logCode += '				}else if(typeof element =="boolean"){		' + '\n'
    logCode += '					if (element){	' + '\n'
    logCode += '						argumertsStr+= key +" : true";	' + '\n'
    logCode += '					}else{' + '\n'
    logCode += '					    argumertsStr+= key +" : false";	' + '\n'
    logCode += '					}' + '\n'
    logCode += '				}else {		' + '\n'
    logCode += '					argumertsStr+= key +" : <"+typeof element+">";	' + '\n'
    logCode += '				}		' + '\n'
    logCode += '				argumertsStr+=" | ";		' + '\n'
    logCode += '			}			' + '\n'
    logCode += '		}				' + '\n'
    logCode += '		return argumertsStr;				' + '\n'
    logCode += '	}					' + '\n'
    logCode += '						' + '\n'
    logCode += '	_global.log=(function(pass_,fileName_,className_,functionName_,argumentObj_,contentObject_){					' + '\n'
    logCode += '		var _lastFileName="";				' + '\n'
    logCode += '		var _logCount=0;				' + '\n'
    logCode += '		var _startLogCount=' + ("%d" % startLogCount_) + ';				' + '\n'
    logCode += '		var _endLogCount=' + ("%d" % endLogCount_) + ';				' + '\n'
    logCode += '		var _lastContentObject=null;				' + '\n'
    logCode += '		return function(pass_,fileName_,className_,functionName_,argumentObj_,contentObject_){				' + '\n'
    logCode += '			_logCount+=1;			' + '\n'
    logCode += '			if(pass_){return};			' + '\n'
    logCode += '			var logStr="";			' + '\n'
    logCode += '			var _strLength=0;			' + '\n'
    logCode += '			var argumentsStr=_global.getPropertys(argumentObj_)			' + '\n'
    logCode += '			if (fileName_ == _lastFileName){' + '\n'
    logCode += '			//if (fileName_ == _lastFileName && this === _lastContentObject){' + '\n'
    logCode += '				if (className_==""){		' + '\n'
    logCode += '					_strLength = String(fileName_+"  ").length;	' + '\n'
    logCode += '				}else{		' + '\n'
    logCode += '					_strLength = String(fileName_+" __ "+className_ +"  ").length;	' + '\n'
    logCode += '				}		' + '\n'
    logCode += '				var spaceStr="";' + '\n'
    logCode += '				for (var i = 0; i<_strLength; i++) {' + '\n'
    logCode += '					spaceStr+=" ";' + '\n'
    logCode += '				}' + '\n'
    logCode += '				logStr=spaceStr + "| "+functionName_+argumentsStr+"    <"+_logCount+">";' + '\n'
    logCode += '			}else{' + '\n'
    logCode += '				lastStrLength_=0;' + '\n'
    logCode += '				if (className_==""){' + '\n'
    logCode += '					logStr = String(fileName_+" __ "+ functionName_+argumentsStr+"    <"+_logCount+">");' + '\n'
    logCode += '				}else{' + '\n'
    logCode += '					logStr = String(fileName_+" __ "+className_ +" __ "+ functionName_+argumentsStr+"    <"+_logCount+">");' + '\n'
    logCode += '				}' + '\n'
    logCode += '			}' + '\n'
    logCode += '			if(_logCount>=_startLogCount&&_logCount<=_endLogCount){' + '\n'
    logCode += '				debug.log(" -- "+logStr);' + '\n'
    logCode += '			}' + '\n'
    logCode += '			if(_logCount>=_startLogCount){' + '\n'
    logCode += '				_lastFileName=fileName_;' + '\n'
    logCode += '			}' + '\n'
    logCode += '			_lastContentObject=contentObject_;' + '\n'
    logCode += '		}' + '\n'
    logCode += '	}());' + '\n'
    logCode += '};' + '\n'
    return logCode

# 为每个函数，添加一个打印输出。
class CocosCreatorCodeAnalyse(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        self._unAnalyseFileList = [
            "/Message/pb.farm.js",
            "/encryption/lib/AES.js",
            "/encryption/lib/BlockModes.js",
            "/encryption/lib/PBKDF2.js",
            "/Message/message.handler.js",
            "/Message/message.parser.js",
            "/Message/message.sender.js",
            "/Message/protocal.js",
            "/Common/protobufjs/minimal/protobuf.js"
            # "/Message/message.event.manager.js",
            # "/Common/event.manager.js",
            # "/Common/event.manager.js",
            # "/Common/http.client.js",
            # "/Common/socket.manager.js",
            # "/Controler/LuckyRedGiftController.js",
            # "/Layer/MainLayer.js",
            # "/LoadScene.js",
            # "/Login/login.js",
            # "/View/InviteRewardView.js",
            # "/Views/BindPublic.js",
            # "/Views/CashTask.js",
            # "/Views/Feedback.js",
            # "/Views/TaskView.js",
            # "/Views/Windfall.js",
            # "/WeChat/share.utils.js",

        ]
        # 只跟踪过滤LOG
        # <开启时，只有_filterLogsDict会显示>
        # <关闭时，在_filterLof>
        self._justFilterLogsBoo = False
        # 需要过滤掉的Log
        self._filterLogsDict = {}
        # 特殊键值显示
        self._specialFuncLogs = {}
        # 是否开启文件名类名的映射
        self._fileNameToObjNameBoo = False
        # 文件名对应的工具类名
        self._fileNameToObjName = {}
        # 限制log输出范围
        self._startLogCount = 0
        self._endLogCount = 99999
        # 测试
        self._assetsFolderPath = self.resPath
        # 实际
        self._assetsFolderPath = "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/"

    def create(self):
        super(CocosCreatorCodeAnalyse, self).create()

        # # json 列表
        # self.displayJsonStructure()
        # return

        # # meta文件中查找UUID
        # self.getMetaByUUID("73bff80e-83db-452b-ad59-7b5fbf67addc")
        # return

        # 1.备份当前文件
        self.recreateJsFileAndBackUp("scripts")
        # 2.删除当前meta
        # self.deleteMata("scripts")
        # 3.解析js并写回文件
        self.analyseJsCode("scripts")
        # 4.打印js结构
        # self.displayJsStructure("scripts")

        # # 指定文件进行解析
        # self.analyseSingle(
        #     "/Volumes/18604037792/develop/ShunYuan/wxGame/assets/scripts/Login/login.js",
        #     "scripts"
        # )

    def destory(self):
        super(CocosCreatorCodeAnalyse, self).destory()

    def getMetaByUUID(self, UUID: str):
        _targetAssetsFolder = fileUtils.getPath(self._assetsFolderPath, "")
        _filePathDict = folderUtils.getFilePathKeyValue(_targetAssetsFolder, [".meta"])
        _find = False
        for _, _filePath in _filePathDict.items():
            _fileMetaDict = fileUtils.dictFromJsonFile(_filePath)
            if _fileMetaDict["uuid"] == UUID:
                print(_filePath)
                _find = True
        if not _find:
            print("uuid {0} none.".format(UUID))


    def displayJsonStructure(self):
        _targetJsonPath = fileUtils.getPath("/Volumes/18604037792/develop/ShunYuan/wxGame/assets/resources/Json/", "")
        _filePathDict = folderUtils.getFilePathKeyValue(_targetJsonPath, [".json"])
        for _keyName, _filePath in _filePathDict.items():
            print(_filePath)

    def recreateJsFileAndBackUp(self, folderName_: str):
        # 目标文件
        _targetJSPath = fileUtils.getPath(self._assetsFolderPath, folderName_)
        # 上层路径
        _targetParentPath = fileUtils.getPath(self._assetsFolderPath, folderName_ + "/..")
        # 备份路径
        _backUpPath = os.path.join(_targetParentPath, os.path.basename(_targetJSPath) + "_backUp")

        # 有备份
        if os.path.exists(_backUpPath):
            # 没有源，有可能删了。【代码执行错误的时候，会删除源，因为，源会变】
            if not os.path.exists(_targetJSPath):
                # 将备份 同步给 源
                shutil.copytree(_backUpPath, _targetJSPath)
                print("备份文件，拷贝回源路径")
            # 源里没有 创建备份的标示。
            if not os.path.isfile(_targetJSPath + '/backup_created'):
                # 删除 原有备份
                shutil.rmtree(_backUpPath)
                # 新备份
                shutil.copytree(_targetJSPath, _backUpPath)
                # 标记已经备份过了
                fileUtils.writeFileWithStr(_targetJSPath + '/backup_created', 'backup end')
            else:
                print("已经创建过备份了")
        else:
            # 没备份文件 - 就备份一份
            shutil.copytree(_targetJSPath, _backUpPath)
            # 标记已经备份过了
            fileUtils.writeFileWithStr(_targetJSPath + '/backup_created', 'backup end')

    def deleteMata(self, folderName_: str):
        _jsCodeFolder = fileUtils.getPath(self._assetsFolderPath, folderName_)
        _filePathDict = folderUtils.getFilePathKeyValue(_jsCodeFolder, [".meta"])
        # 移除掉无用的meta文件
        for _keyName, _filePath in _filePathDict.items():
            fileUtils.removeExistFile(_filePath, True)

    def displayJsStructure(self, folderName_: str):
        _jsCodeFolder = fileUtils.getPath(self._assetsFolderPath, folderName_)
        _filePathDict = folderUtils.getFilePathKeyValue(_jsCodeFolder, [".js"])
        for _keyName, _filePath in _filePathDict.items():
            print(_filePath)

    def analyseJsCode(self, folderName_: str):
        _jsCodeFolder = fileUtils.getPath(self._assetsFolderPath, folderName_)
        _filePathDict = folderUtils.getFilePathKeyValue(_jsCodeFolder, [".js"])
        # 代码中使用function的次数
        _funcLineCount = 0

        # 正则表达式队列
        for _, _filePath in _filePathDict.items():
            # 做判断的,用来显示的路径
            fileShowName = _filePath.split(folderName_)[1]
            if fileShowName in self._unAnalyseFileList:
                continue
            _funcLineCount += self.analyseSingle(_filePath, folderName_)

        print('共有 {0} 处function使用'.format(_funcLineCount))

    def analyseSingle(self, filePath_: str, folderName_: str):
        _funcLineCount = 0
        # 做判断的,用来显示的路径
        fileShowName = filePath_.split(folderName_)[1]

        # 实质内容的行数
        currentLine = 0
        # 行数
        lineCount = 0
        # 多行注释堆栈
        multiCommon = False
        # 记录判断修改后的行
        jsLines = []
        # 读每一行
        jsCodes = fileUtils.linesFromFile(filePath_)

        # 逐行循环
        for jsLine in jsCodes:
            # 记录行号
            lineCount = lineCount + 1
            # 临时的行副本
            tempJsLine = jsLine

            # 多行注释/*...
            if multiCommon == False:
                commonMatchBegin = re.search(r'/\*.*', tempJsLine)
                if commonMatchBegin:
                    # /* ... */
                    commonMatchOneLine = re.search(r'/\*.*\*/(.*)', tempJsLine)
                    if commonMatchOneLine:
                        multiCommon = False
                        tempJsLine = commonMatchOneLine.group(1)
                    else:
                        multiCommon = True
                        tempJsLine = ''
            else:
                # ...*/
                commonMatchEnd = re.search(r'.*\*/(.*)', tempJsLine)
                if commonMatchEnd:
                    multiCommon = False
                    tempJsLine = commonMatchEnd.group(1)
            if multiCommon:
                # 处于多行注释,相当于代码是空行
                jsLine = "\n"
                jsLines.append(jsLine)
                continue

            # 单行注释
            commonMatch = re.search(r'(.*)//.*', tempJsLine)

            if commonMatch:
                # 排除网址,最后一个字符为\这样的字符串拼接.字符串拼接里面的//不是代码的注释,是字符串的一部分.
                if tempJsLine.find("http://") < 0 and \
                        tempJsLine.find("https://") < 0 and \
                        tempJsLine.strip()[len(tempJsLine.strip()) - 1] != "\\" and \
                        tempJsLine.find("wss://") < 0 and \
                        tempJsLine.find("ws://") < 0:
                    tempJsLine = commonMatch.group(1)
                    # 分割注释,提取非注释部分
                    jsLine = tempJsLine + "\n"
                    # 去空格及特殊符号
                    tempJsLine = tempJsLine.strip()

            # 去掉空白行
            if tempJsLine.strip() == '':
                jsLines.append("\n")
                continue

                # 不考虑 '...function...' 以及 "...function..." 的情况。。。

            # 有实质内容，行数叠加
            currentLine = currentLine + 1

            # log取得
            logMatch = re.search(r'(.*)cc\.log\(.*\);?(.*)', tempJsLine)
            # 含log
            if logMatch:
                # 去掉原有log
                jsLine = logMatch.group(1) + logMatch.group(2)
            # log取得
            logMatch = re.search(r'(.*)console\.log\(.*\);?(.*)', tempJsLine)
            # 含log
            if logMatch:
                # 去掉原有log
                jsLine = logMatch.group(1) + logMatch.group(2)

            # log取得
            logMatch = re.search(r'(.*)window\.debug\.log\(.*\);?(.*)', tempJsLine)
            # 含log
            if logMatch:
                # 去掉原有log
                jsLine = logMatch.group(1) + logMatch.group(2)
            else:
                logMatch = re.search(r'(.*)debug\.log\(.*\);?(.*)', tempJsLine)
                # 含log
                if logMatch:
                    # 去掉原有log
                    jsLine = logMatch.group(1) + logMatch.group(2)

            # 用于 new Function 的方式。工程内没有
            # functionBigMatch=re.search(r'(.*)Function(.*)',tempJsLine)
            # if functionBigMatch:
            #     print tempJsLine

            functionMatch = re.search(r'.*function.*\(.*\).*', tempJsLine)
            if functionMatch:
                # 工程里有/function\s*([^(]*)\(/ 这个正则表达式 规避掉这个情况
                if tempJsLine.find('match(/function\s*([^(]*)\(/)') < 0:
                    # 记录Function数量
                    _funcLineCount = _funcLineCount + 1
                    functionName = ''
                    arguments = ''
                    functionOneLine_1 = re.search(r'.*function\s*(.*)\s*\(\s*.*\s*\)\s*\{.*', tempJsLine)
                    if functionOneLine_1:
                        # xx:function(xx){
                        functionOneLine_2 = re.search(r'\s*(.*)\s*:\s*function\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                        if functionOneLine_2:
                            functionName = functionOneLine_2.group(1)
                            arguments = functionOneLine_2.group(2)
                        else:
                            # * (function(){
                            functionOneLine_3 = re.search(r'.*\(\s*function\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                            if functionOneLine_3:
                                if tempJsLine.strip() == '(function(){':
                                    # 就是初始化用的
                                    functionName = "__init__"
                                    arguments = functionOneLine_3.group(1)
                                else:
                                    # ty.PublishersManager = (function(){
                                    functionOneLine_4 = re.search(
                                        r'\s*(.*)\s*=\s*\(\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                        tempJsLine)
                                    if functionOneLine_4:
                                        functionName = functionOneLine_4.group(1)
                                        arguments = functionOneLine_4.group(2)
                                    else:
                                        #       this.view.ccbRootNode.setOnExitCallback(function(){
                                        functionOneLine_5 = re.search(
                                            r'\s*(.*)\(\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                            tempJsLine)
                                        if functionOneLine_5:
                                            functionName = functionOneLine_5.group(1)
                                            arguments = functionOneLine_5.group(2)
                            else:
                                # ty.PublishersManager = function(){
                                functionOneLine_6 = re.search(r'\s*(.*)\s*=\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                                              tempJsLine)
                                if functionOneLine_6:
                                    # var sss = function(){
                                    functionOneLine_7 = re.search(
                                        r'\s*var\s*(.*)\s*=\s*function\s*\(\s*(.*)\s*\)\s*\{.*',
                                        tempJsLine)
                                    if functionOneLine_7:
                                        functionName = "var_" + functionOneLine_7.group(1)
                                        arguments = functionOneLine_7.group(2)
                                    else:
                                        functionName = functionOneLine_6.group(1)
                                        arguments = functionOneLine_6.group(2)
                    else:
                        functionOneLine_11 = re.search(r'\s*function\s*(.*)\s*\(\s*(.*)\s*\)\s*\{.*', tempJsLine)
                        if functionOneLine_11:
                            functionName = functionOneLine_11.group(1)
                            arguments = functionOneLine_11.group(2)
                    if functionName.strip() == '':
                        # function xx(){ 这样的全局函数。
                        jsLines.append(jsLine)
                        print("{0} _ {1} _ 类似全局函数，或者特殊写法，未添加log".format(fileShowName, jsLine.split('\n'[0])))
                    else:
                        # 去掉没过滤好的空格
                        functionName = functionName.strip()
                        # 拆分模式
                        replace = re.search(r'(.*function.*\(.*\).*\{)(.*)', jsLine)

                        # 整理参数-让参数 得以在运行时输出成对应值
                        argumentsStr = '{'
                        argumentsList = arguments.split(",")
                        for arg_i in range(len(argumentsList)):
                            argument = argumentsList[arg_i].strip()
                            if argument == '':
                                continue
                            else:
                                argumentsStr += '"' + argument + '":' + argument + ','
                        argumentsStr += '}'

                        # 折射全局对象名-全局函数的文件不输出js路径，而是输出自己的全局类名
                        className = ''
                        if self._fileNameToObjNameBoo:
                            # 存在对应关系就转换
                            if fileShowName in self._fileNameToObjName:
                                className = self._fileNameToObjName[fileShowName]
                        # 函数名有 ' 的话,把 ' 转意了.
                        if functionName.find("\'") > 0:
                            functionName = "\\\'".join(functionName.split("'"))

                        # 是否需要过滤-运行时，取得这个作为参数，决定是否显示log
                        passBooStr = 'false'
                        if self._justFilterLogsBoo:
                            # 只过滤
                            passBooStr = 'true'
                            if fileShowName in self._filterLogsDict:
                                passBooStr = 'false'
                                print("{0} _ {1} _会输出".format(fileShowName, functionName))
                        else:
                            # 只显示
                            if passBooStr == 'false':
                                changeBoo = True
                                if fileShowName in self._filterLogsDict:
                                    if functionName in self._filterLogsDict[fileShowName]:
                                        changeBoo = False
                                if changeBoo == False:
                                    passBooStr = 'true'
                                    print("{0} _ {1} _输出被过滤".format(fileShowName, functionName))
                            if (fileShowName + ' -> ' + functionName) in self._specialFuncLogs:
                                functionName = self._specialFuncLogs[fileShowName + ' -> ' + functionName]
                        newJsLine = replace.group(
                            1) + '\n' + '_global.log(' + passBooStr + ',\'' + fileShowName.ljust(
                            45) + '\',\'' + className.rjust(
                            25) + '\',\'' + functionName + '\',' + argumentsStr + ');\n' + replace.group(2)
                        # 修改后的
                        jsLines.append(newJsLine)
                else:
                    # 使用Function做正则表达式的行
                    jsLines.append(jsLine)
            else:
                # 非function行
                jsLines.append(jsLine)

        if (len(jsLines) != lineCount):
            print('识别行数与给定行数不一致 : {0} {1} - {2}'.format(fileShowName, len(jsLines), lineCount))
        else:
            # 如果存在任意一行的话
            if len(jsLines) > 0:
                jsLines[0] = jsLines[0].split('\n')[0] + '\n'
                jsLines.insert(0, addLogFun(self._startLogCount, self._endLogCount))
                jsCodeStr = "".join(jsLines)
                # 写一个新的
                fileUtils.writeFileWithStr(filePath_, jsCodeStr)

        return _funcLineCount
