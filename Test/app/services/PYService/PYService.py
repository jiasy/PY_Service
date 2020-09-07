#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from base.supports.Base.Base import Base
from base.app.services.base.DataCenter.DataBindings.DataCompare import DataCompare
from base.app.services.base.DataCenter.DataBindings.DataConnector import DataConnector
from utils import *
import json


class PYService(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(PYService, self).create()
        self.doTest()

    def destory(self):
        super(PYService, self).destory()

    def doTest(self):
        _jsonStr = '{"result":1245186,"roomCardCount":1000000,"battleId":0,"roomId":0,"marqueeVersion":{"low":1,"high":0,"unsigned":false},"newMail":null,"newLimitedCostlessActivity":false,"noticeVersion":{"low":0,"high":0,"unsigned":false},"activityInfo":[{"id":300001,"startTime":{"low":-576284416,"high":345,"unsigned":false},"endTime":{"low":-72284416,"high":345,"unsigned":false}},{"id":300005,"startTime":{"low":-224153600,"high":349,"unsigned":false},"endTime":{"low":438245400,"high":350,"unsigned":false}},{"id":300008,"startTime":{"low":-2140022784,"high":353,"unsigned":false},"endTime":{"low":-238493672,"high":133356,"unsigned":false}},{"id":300004,"startTime":{"low":-1994684416,"high":345,"unsigned":false},"endTime":{"low":-1908285416,"high":345,"unsigned":false}},{"id":300002,"startTime":{"low":131409920,"high":355,"unsigned":false},"endTime":{"low":217808920,"high":355,"unsigned":false}},{"id":300007,"startTime":{"low":-2140022784,"high":353,"unsigned":false},"endTime":{"low":-584823784,"high":353,"unsigned":false}},{"id":300000,"startTime":{"low":-576284416,"high":345,"unsigned":false},"endTime":{"low":46435072,"high":368,"unsigned":false}}],"buttonValue":13,"timeStamp":{"low":1316055502,"high":355,"unsigned":false},"clubId":null,"createTime":{"low":1037369829,"high":355,"unsigned":false},"connGroup":"c74d97b01eae257e44aa9d5bade97baf","isIdentityVerify":false,"isAgency":false,"agtWebUrl":"","combatId":0,"area":10002,"displayId":5198814,"mttStartTime":{"low":0,"high":0,"unsigned":false},"ticket":0,"phone":"","notifyRedDot":[],"pushRegisterId":""}';
        _jsonDict = json.loads(_jsonStr)

        # # 输出结构
        # print('dictUtils.showDict(_jsonDict) : ----------------------------------')
        # dictUtils.showDictStructure(_jsonDict)

        # 设置数据，经过转化
        _changeList = self.sm.dc.sv("user", _jsonDict)
        # 输出数据变化过的路径
        print('_changeList = ')
        for _i in range(len(_changeList)):
            print('_changeList['+str(_i)+'] = ' + str(_changeList[_i]))

        # # 转化过的数据，在序列化成字符串
        # _dataSetStr = str(json.dumps(self.sm.dc.ds, indent=4, sort_keys=False, ensure_ascii=False))
        # print('_dataSetStr = \n' + str(_dataSetStr))

        # 取得没有转换的源数据
        _activityInfoList = self.sm.dc.listDict["user.activityInfo"]
        print('_activityInfoList = \n' + str(_activityInfoList))
        print('self.sm.dc.ds.activityInfo = ' + str(self.sm.dc.ds["user"]["activityInfo"]))

        # 用于数据比较的数据绑定 -----------------------------------------------------------------
        _dataCompare = DataCompare(self.sm)
        _dataCompare.create()
        print(_dataCompare.resetByStr("user.result>=1")[1])
        print(_dataCompare.resetByStr("user.result<1")[1])

        # 用于字符串显示的数据绑定 ---------------------------------------------------------------
        _dataConnector = DataConnector(self.sm)
        _dataConnector.create()
        # 数组中某一项通过字符串拼接的方式获取其中内容
        _idx = 5
        _propertyName = "user.activityInfo"
        _propertyNameOfIdx = _propertyName + "___" + str(_idx + 1)
        print(_dataConnector.resetByStr("当前的第" + str(_idx + 1) + "个活动Id:${" + _propertyNameOfIdx + ".id}")[1])
        # 以某一个层级获取到的数据对象为起始点，通过 相对数据路径 取 数据
        _activityDict = self.sm.dc.getListElementByIdx("user.activityInfo", _idx)
        _startTime_low = self.sm.dc.gv("startTime.low", _activityDict)
        print("_startTime_low = " + str(_startTime_low))

        # 通过拼接方式，获取字符串的值，重置当前监听路径，获取拼接后的字符串
        print(_dataConnector.resetByStr("当前房间ID:${user.roomId}")[1])
