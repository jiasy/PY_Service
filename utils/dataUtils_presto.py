# !/usr/bin/env python3

import re
import json

import utils.sqlDataUtils
import utils.pyUtils

from pyhive import hive
from pyhive import presto  # or import hive
from pyhive.presto import Connection, Cursor

"""
# 阿里 链接信息
_alPrestoInfo = dict(
    {
        "host": "123.206.114.114",
        "port": "8080",
        "catalog": "hive", # 库名
        "serverName": "ALi", # server 类型，用来标注是哪个数据库的，
        "schema": 'ods', # schema名称
        'schemaList': ["mjdw", "mjdm", "ods"] # 库中存在的schema列表 
    }
)

"""


# 获取数据库连接
def getConnectionAndCursor(
        type_: str,
        host: str,
        port: str,
        catalog: str,
        schema: str,
        username: str = None,
        password: str = None,
        **otherParamters
):
    _connection: Connection = None
    _cursor: Cursor = None
    if type_ == "presto":
        '''
            presto.connect 支持的参数
                host, port = "8080", 
                username = None, 
                catalog = 'hive',
                schema = 'default', 
                poll_interval = 1, 
                source = 'pyhive', s
                ession_props = None,
                protocol = 'http', 
                password = None, 
                requests_session = None, 
                requests_kwargs = None
        '''
        _connection = presto.connect(
            host=host, port=port, username=username, password=password, catalog=catalog, schema=schema
        )
        _cursor = _connection.cursor()
    elif type_ == "hive":
        _connection = hive.connect(
            host=host, port=port, username=username, password=password, catalog=catalog, schema=schema
        )
        _cursor = _connection.cursor()
    else:
        raise utils.pyUtils.AppError("type_ " + type_ + " is unexpected")
    return _connection, _cursor


# 通过presto的链接信息去链接并执行Sql
def executePrestoSQL(prestoInfo_, sql_):
    # 获取 数据库 链接
    _connection, _cursor = getConnectionAndCursor("presto", **prestoInfo_)
    return utils.sqlDataUtils.executeSQL(_cursor, sql_)
