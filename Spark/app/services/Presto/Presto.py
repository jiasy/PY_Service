#!/usr/bin/env python3
from TCLIService.ttypes import TOperationState

from base.supports.Service.BaseService import BaseService
from utils import dataUtils_presto
from utils import sqlDataUtils
from utils import listUtils
from sqlalchemy.engine import create_engine
import pandas as pd
from pyhive.presto import Cursor


class Presto(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(Presto, self).create()

        # 腾讯 链接信息
        _txPrestoInfo = dict(
            {
                'host': 'ip',
                'port': '端口',
                'catalog': 'hive',
                'serverName': 'TengXun',
                'schemaList': ["mjdw", "mjdm", "ods"]
            }
        )

        # 阿里 链接信息
        _alPrestoInfo = dict(
            {
                "host": "ip",
                "port": "端口",
                "catalog": "hive",
                "serverName": "ALi",
                'schemaList': ["mjdw", "mjdm", "ods"]
            }
        )

        # 指定当前配置
        _prestoInfo = _txPrestoInfo

        # schema的列表
        _schemaList = _prestoInfo["schemaList"]
        # 默认查询的 schema
        _prestoInfo["schema"] = _schemaList[0]

        # # ----------------------------------------------------------------------------------------------
        # # 输出所有表的结构描述
        # _tableDescribeInfoDict = self.getAllSchemaTableDescribeInfo(_prestoInfo, _schemaList)
        # # 输出所有表的行数
        # _tableRowCountDict = self.getAllSchemaTableRowCount(_prestoInfo, _schemaList)
        #
        # for _schema, _tableDescribeInfoList in _tableDescribeInfoDict.items():
        #     _tableRowCountList = _tableRowCountDict[_schema]
        #     for _tableDescribeInfo in _tableDescribeInfoList:
        #         for _tableRowCount in _tableRowCountList:
        #             if _tableDescribeInfo["tableName"] == _tableRowCount["tableName"]:
        #                 _tableDescribeInfo["rowCount"] = _tableRowCount["rowCount"]
        # # 保存到本地
        # fileUtils.writeFileWithStr(
        #     fileUtils.getPath(self.resPath, _prestoInfo["serverName"]+"TableDescribInfo.json"),
        #     str(json.dumps(_tableDescribeInfoDict, indent=4, sort_keys=False, ensure_ascii=False))
        # )

        '''
            结构
            +--schema 名称 [0]
            |      +--tableName
            |      +--fields [0]
            |      |      +--name
            |      |      +--type
            |      |      +--comment
            |      +--rowCount
        '''
        # # ----------------------------------------------------------------------------------------------
        # # 从本地加载，预存的表结构描述
        # _tableDescribeInfoCache = fileUtils.dictFromJsonFile(
        #     fileUtils.getPath(
        #         self.resPath,
        #         _prestoInfo["serverName"] + "TableDescribInfo.json"
        #     )
        # )
        #
        # # 显示结构
        # dictUtils.showDictStructure(_tableDescribeInfoCache)
        # # # 分析表结构
        # self.analyseTableDescribe(_tableDescribeInfoCache)

        # ----------------------------------------------------------------------------------------------
        # # 表结构 转换成 表的创建语句
        # self.sm.presto.allTablesToCreateSQL(_prestoInfo)
        # # 链接 Presto 查找数据
        # self.sm.presto.getDataFrameFromPresto(
        #     _prestoInfo,
        #     "dw_dim_agency",
        #     ["agency_id", "reg_time"],
        #     10
        # )

    # -------------------------------------------------------------------------------------------------------
    #         _sql = '''
    # select
    #   log_date,
    #   sub_area_id,
    #   gold_room_type,
    #   (case when gold_applied_num = null then 0 else sum(gold_applied_num) end)+
    #   (case when system_total_pay = null then 0 else sum(system_total_pay) end)+
    #   (case when mulit_entry_pay = null then 0 else sum(mulit_entry_pay) end)+
    #   (case when high_power_service = null then 0 else sum(high_power_service) end)+
    #   (case when guess_chicken_cost_gold = null then 0 else sum(guess_chicken_cost_gold) end)+
    #   (case when guess_chicken_win_gold = null then 0 else sum(guess_chicken_win_gold) end)
    #   -- ifnull(sum(gold_applied_num),0)+
    #   -- ifnull(sum(system_total_pay),0)+
    #   -- ifnull(sum(mulit_entry_pay),0)+
    #   -- ifnull(sum(high_power_service),0)+
    #   -- ifnull(sum(guess_chicken_cost_gold),0)+
    #   -- ifnull(sum(guess_chicken_win_gold),0)
    # from
    #   gold_statistics
    # where
    #   log_date= date '2019-01-01'
    # GROUP BY
    #   log_date,
    #   sub_area_id,
    #   gold_room_type
    #         '''
    #         _prestoInfo["schema"] = "ods"
    #         _info = dataPrestoUtils.executePrestoSQL(_prestoInfo, _sql)
    #         print('_info = ' + str(_info))

    def destory(self):
        super(Presto, self).destory()

    # 获取当前连接下所有表结构
    '''
        结构如下
            +-- [0]
            |      +--tableName
            |      +--fields [0]
            |      |      +--name
            |      |      +--type
            |      |      +--comment
    '''

    def getTableInfoList(self, cursor_: Cursor, catalog_: str, schema_: str):
        _tableDescribeInfoList = []
        _tableNameList = self.getTableNameList(cursor_)
        for _i in range(len(_tableNameList)):
            _tableName = _tableNameList[_i]
            _tableDescribeInfo = self.getTableDescribe(cursor_, catalog_, schema_, _tableName)
            _tableDescribeInfoList.append(_tableDescribeInfo)
        return _tableDescribeInfoList

    # 获取数据库的所有表名
    def getTableNameList(self, cursor_: Cursor):
        _showTablesSQL = "show tables"
        _tableNames, _errList = sqlDataUtils.executeSQL(cursor_, _showTablesSQL)
        return [_tableTuple[0] for _tableTuple in _tableNames]

    # 获取表的结构描述
    def getTableDescribe(self, cursor_: Cursor, catalog_: str, schema_: str, tableName_: str):
        _descTableSQL = "describe " + tableName_
        _fatchAll, _errList = sqlDataUtils.executeSQL(cursor_, _descTableSQL)
        _tableDescribeInfo = self.table_describe_info(catalog_, schema_, tableName_, _fatchAll)
        return _tableDescribeInfo

    # 通过表的结构描述，变换成表的创建语句
    def tableDescribeToCreateSQL(self, tableDescribeInfo_: dict):
        _replaceInfo = dict({})
        _replaceInfo["tableName"] = tableDescribeInfo_["tableName"]
        _fieldList = tableDescribeInfo_["fields"]
        _fieldStrList = []
        for _i in range(len(_fieldList)):
            _field = _fieldList[_i]
            _fieldStr = _field["name"] + " " + _field["type"] + ' comment \'' + _field["comment"] + '\''
            _fieldStrList.append(_fieldStr)
        _fieldStr = ','.join(_fieldStrList)
        _replaceInfo["fields"] = _fieldStr
        return "CREATE TABLE {tableName}({fields}) COMMENT '' WITH (format = 'ORC');".format(**_replaceInfo)

    # 将获取到表结构信息结构化
    def table_describe_info(self, catalog_: str, schema_: str, tableName_: str, fetchallInfos_: list):
        _describleInfo = dict({})
        _describleInfo["tableName"] = catalog_ + "." + schema_ + "." + tableName_
        _fields = []
        _describleInfo["fields"] = _fields
        for _i in range(len(fetchallInfos_)):
            _fieldTuple = fetchallInfos_[_i]
            _field = dict({})
            _field["name"] = _fieldTuple[0]
            _field["type"] = _fieldTuple[1]
            _field["comment"] = _fieldTuple[3]
            _fields.append(_field)
        return _describleInfo

    # 输出所有 schema 下的表的数据数量
    def getAllSchemaTableRowCount(self, prestoInfo_: dict, schemaList_: list):
        _tableRowCountInfoDict = dict({})

        # 输出表的表的数据数
        def printTableRowCountInfo(tableRowCountInfoList_):
            # 输出表的数据数量
            for _i in range(len(tableRowCountInfoList_)):
                _info = tableRowCountInfoList_[_i]
                print(str(_i) + " : " + _info['tableName'].ljust(40) + str(_info['rowCount']).rjust(12))

        for _schema in schemaList_:
            # 修改 目标 Schema
            prestoInfo_["schema"] = _schema
            # 获取 schema 下的所有表，行数信息
            _tableRowCountInfoList = self.allTableRowCountInfoList(prestoInfo_)
            _tableRowCountInfoDict[_schema] = _tableRowCountInfoList
            # # 输出信息
            # print("schema : " + _schema + " ------------------------------------")
            # printTableRowCountInfo(_tableRowCountInfo)
        return _tableRowCountInfoDict

    # 打印所有schema的表字段信息
    def getAllSchemaTableDescribeInfo(self, prestoInfo_: dict, schemaList_: list):
        _tableInfoDict = dict({})
        for _schema in schemaList_:
            # 修改 目标 Schema
            prestoInfo_["schema"] = _schema
            # 获取 数据库 链接
            _connection, _cursor = dataUtils_presto.getConnectionAndCursor("presto", **prestoInfo_)
            # 获取当前数据库的表的字段信息
            _tableDescribeInfoList = self.getTableInfoList(_cursor, prestoInfo_["catalog"], prestoInfo_["schema"])
            _tableInfoDict[_schema] = _tableDescribeInfoList
        # # 输出成字符串
        # print(str(json.dumps(_tableInfoDict, indent=4, sort_keys=False, ensure_ascii=False)))
        return _tableInfoDict

    # 每个表有多少数据
    def allTableRowCountInfoList(self, prestoInfo_: dict):
        # 获取 数据库 链接
        _connection, _cursor = dataUtils_presto.getConnectionAndCursor("presto", **prestoInfo_)
        _tableNameList = self.getTableNameList(_cursor)
        _tableRowCountInfoList = []
        for _i in range(len(_tableNameList)):
            _tableName = _tableNameList[_i]
            # count(*) 不是"计算所有的字段"，会把*解析成 “一条数据” 的意思。
            _countSQL = "select count(*) from " + _tableName
            # 完整的表名
            _fullTableName = '{catalog}.{schema}.{tableName}'.format(
                catalog=prestoInfo_['catalog'],
                schema=prestoInfo_["schema"],
                tableName=_tableName
            )
            # print('counting : ' + _fullTableName)
            # 返回数据 [(行数,)]
            _countInfo, _errList = sqlDataUtils.executeSQL(_cursor, _countSQL)
            _dict = dict({})
            _dict["tableName"] = _fullTableName
            _dict["rowCount"] = int(_countInfo[0][0])
            _tableRowCountInfoList.append(_dict)
            # 排序
            listUtils.sortListOfDict(_tableRowCountInfoList, "rowCount")
        return _tableRowCountInfoList

    # 所有表结构解析，创建对应的生成语句
    def allTablesToCreateSQL(self, prestoInfo_: dict):
        # _table_info = {
        #     'catalog': 'hive',
        #     'schema': 'mjdm',
        #     'table': 'DM_player_round_D'
        # }
        #
        # delSQL = "DELETE FROM {catalog}.{schema}.{table} WHERE gen_date = '2018-12-25'".format(**_table_info)

        # 获取 数据库 链接
        _connection, _cursor = dataUtils_presto.getConnectionAndCursor("presto", **prestoInfo_)
        # 获取当前数据库的表的字段信息
        _tableDescribeInfoList = self.getTableInfoList(_cursor, prestoInfo_["catalog"], prestoInfo_["schema"])
        if _tableDescribeInfoList:
            for _i in range(len(_tableDescribeInfoList)):
                _tableDescribeInfo = _tableDescribeInfoList[_i]
                _createSQL = self.tableDescribeToCreateSQL(_tableDescribeInfo)
                print('_createSQL = ' + str(_createSQL))

    # 获取数据
    def getDataFrameFromPresto(self, prestoInfo_: dict, tableName_: str, fields_: list = None, limit_: int = None):
        # Presto
        _presto_url = 'presto://{host}:{port}/{catalog}/{schema}'.format(**prestoInfo_)
        # host是服务器ip，port是端口，hive指的是Presto的catalog，my_schema是hive的schema
        _engine = create_engine(_presto_url)
        # 拼接要查找的字段
        _fieldsStr = "*"
        if fields_:
            _fieldsStr = ",".join(fields_)
        # 拼接条数限制
        _limitStr = ""
        if limit_:
            _limitStr = " limit " + str(limit_)
        # 一般pandas从数据库中读取数据无任何区别，分析师们应该非常熟悉了。
        df = pd.read_sql("select " + _fieldsStr + " from " + tableName_ + _limitStr, _engine)
        print(df)

    # 分析所有数据
    def analyseTableDescribe(self, tableDescribeInfo_):
        def subPrint(count_, schema_, table_, field_, logStr_):
            print("<" + count_ + "> " + schema_ + "." + table_ + "." + field_ + " : " + logStr_)

        for _schema, _tableDescribeInfoList in tableDescribeInfo_.items():
            # print('_schema = ' + str(_schema))
            for _tableDescribeInfo in _tableDescribeInfoList:
                # 每一个表中应当都有一个时间相关的东西吧
                _has_gen_date = False
                _has_log_time = False
                _tableName = _tableDescribeInfo["tableName"]
                _fields = _tableDescribeInfo["fields"]
                _count = str(_tableDescribeInfo["rowCount"])
                # print('  _tableName = ' + str(_tableName))
                for _field in _fields:
                    _fieldName = _field["name"]
                    _fieldType = _field["type"]
                    _fieldComment = _field["comment"]
                    # print('    _fieldName = ' + str(_fieldName))
                    if _fieldName == "gen_date":
                        _has_gen_date = True
                        if not _fieldType == "date":
                            subPrint(_count, _schema, _tableName, _fieldName, "gent_date 数据格式 : " + _fieldType)
                    if _fieldName == "log_time":
                        _has_log_time = True
                        if not _fieldType == "timestamp":
                            subPrint(_count, _schema, _tableName, _fieldName, "log_time 数据格式为 : " + _fieldType)

                if not _has_gen_date and not _has_log_time:
                    subPrint(_count, _schema, _tableName, _fieldName, "没有 gen_date 或者 log_time ")
                    for _field in _fields:
                        print("  " + _field["name"])
