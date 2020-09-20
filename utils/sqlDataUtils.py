# !/usr/bin/env python3

import re
import json
import utils.dictUtils

from pyhive.presto import Connection, Cursor


# 执行 sql语句
def executeSQL(cursor_: Cursor, SQL_: str):
    # print("executeSQL : " + str(SQL_))
    try:
        cursor_.execute(SQL_)
        _fetchall = cursor_.fetchall()
        # print(_fetchall)
        return _fetchall, None
    except Exception as e:
        # print("ERROR : ")
        # print('%s' % str(json.dumps(e.args, indent=4, sort_keys=False, ensure_ascii=False)))
        # utils.dictUtils.showDictStructure(e.args)
        return None, [_arg["message"] for _arg in e.args]
    finally:
        cursor_.close()
