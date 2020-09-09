#!/usr/bin/env python3
# Created by jiasy at 2019/1/29
from base.supports.Base.BaseInService import BaseInService
from utils import pyUtils
from utils import fileUtils
from utils import dataUtils_presto


class OLAP_assets_statistics_D(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)
        self.sqlFilePath = fileUtils.getPath(self.resPath, self.className + ".sql")

    def create(self):
        super(OLAP_assets_statistics_D, self).create()

    def destory(self):
        super(OLAP_assets_statistics_D, self).destory()

    def getAllRelationTableInfo(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        # 读取sql内容
        _sqlStr = fileUtils.readFromFile(self.sqlFilePath)

        # print('_sqlStr = ' + str(_sqlStr))
        # _sqlWithOutComment = codeUtils.removeComment("sql", _sqlStr)
        # print('_sqlWithOutComment = ' + str(_sqlWithOutComment))
        # # 去掉注释切分Sql输出查看每一个SQL
        # _sqlList = _sqlWithOutComment.split(";")
        # for _i in range(len(_sqlList)):
        #     print('_sqlList[_i] = \n' + str(_sqlList[_i]))

        # 获取表和表中索取字段
        _whatFromWhereInfo = self.belongToService.getSelectWhatFromWhere(_sqlStr)
        # 获取要执行的Sql列表
        _sqlList = self.belongToService.whatFromWhereToQuerySqlList(_whatFromWhereInfo)

        # 腾讯 链接信息
        _txPrestoInfo = dict(
            {
                'host': 'ip',
                'port': 'port',
                'catalog': 'hive',
                'serverName': 'TengXun',
                'schema': 'olap'
            }
        )

        # 执行的sql列表输出，链接 presto 来执行这些 Sql 语句
        for _i in range(len(_sqlList)):
            _querySql = _sqlList[_i]
            _result, _errList = dataUtils_presto.executePrestoSQL(_txPrestoInfo, _querySql)
            if _errList:
                print(_querySql)
                print("ERROR : \n" + str(_errList))
            else:
                if len(_result) == 0:
                    print(_querySql)
                    print('WARNING : no data')
