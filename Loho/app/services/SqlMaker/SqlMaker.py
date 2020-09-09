#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import listUtils
from utils import codeUtils
from utils import codeUtils_sql
from utils import timeUtils

import json


class SqlMaker(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(SqlMaker, self).create()
        self.getSubClassObject("OLAP_goldroom_D")
        self.getSubClassObject("OLAP_chuanqi_D")
        self.getSubClassObject("OLAP_assets_statistics_D")

        self.oLAP_goldroom_D.getAllRelationTableInfo()
        self.oLAP_assets_statistics_D.getAllRelationTableInfo()

    def destory(self):
        super(SqlMaker, self).destory()

    def whatFormWhereCollection(self, selectTableInfo_: dict, collectionInfo_: dict, tableKey_: str, fieldKey_: str):
        if tableKey_ in selectTableInfo_:
            _tableName = selectTableInfo_[tableKey_]
            _selectFields = selectTableInfo_[fieldKey_]
            if not _tableName in collectionInfo_:
                collectionInfo_[_tableName] = []
            collectionInfo_[_tableName] = listUtils.unionTwoList(collectionInfo_[_tableName], _selectFields)

    # 从sql 中获取要从那些表取得那些数据
    def getSelectWhatFromWhere(self, sqlStr_):
        _whatFromWhereInfo = dict({})
        _sqlStr = sqlStr_
        _sqls = codeUtils.removeComment("sql", _sqlStr).split(";")
        for _i, _sql in enumerate(_sqls):
            if not _sql.strip() == "":
                # 解析sql,得到他从哪些表获取了哪些字段
                _selectTableInfo = codeUtils_sql.analyseSql(_sql)
                self.whatFormWhereCollection(
                    _selectTableInfo, _whatFromWhereInfo, "selectTableA", "selectFieldsA"
                )
                self.whatFormWhereCollection(
                    _selectTableInfo, _whatFromWhereInfo, "selectTableB", "selectFieldsB"
                )
                self.whatFormWhereCollection(
                    _selectTableInfo, _whatFromWhereInfo, "selectTable", "selectFields"
                )
        print(str(json.dumps(_whatFromWhereInfo, indent=4, sort_keys=False, ensure_ascii=False)))

        return _whatFromWhereInfo

    # 组装成 sql 查询语句，并且在有 gen_date 的情况下只查询当天的数据，查一条即可
    def whatFromWhereToQuerySqlList(self, whatFromWhereInfo_):
        _sqlList = []
        for _tableName in whatFromWhereInfo_:
            _fields = whatFromWhereInfo_[_tableName]
            _sql = None
            if "gen_date" in _fields:
                _sql = """select {fields} from {tableName} where gen_date = date('{day}') limit 1""".format(
                    fields=",".join(_fields),
                    tableName=_tableName,
                    day=timeUtils.getDayFromToday(-1)
                )
            else:
                _sql = """select {fields} from {tableName} limit 1""".format(
                    fields=",".join(_fields),
                    tableName=_tableName
                )
            _sqlList.append(_sql)
        return _sqlList
