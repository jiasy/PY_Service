# !/usr/bin/env python3

import re
import json

import utils.strUtils
import utils.codeUtils


# 将多行的sql转换成一行，然后统一用空格分割语句，将与括号链接的字符和括号分割开，这样可以不用区分可能有可能没有的空格和括号的关系
def sqlInOneLine(sqlStr_: str):
    # 多行变成一行
    _sqlInOneLine = ' '.join(sqlStr_.split("\n"))
    _sqlInOneLine = utils.codeUtils.addSpaceInCharBracket(_sqlInOneLine)
    # 多个空格相邻变成一个空格
    _sqlInOneLine = utils.strUtils.spacesReplaceToSpace(_sqlInOneLine)
    return _sqlInOneLine


# 解析sql语句，获取相关信息
def analyseSql(sqlStr_: str):
    _selectTableInfo = dict({})
    # 移除注释
    _sql = utils.codeUtils.removeComment("sql", sqlStr_)
    # 整理成一行
    _sql = sqlInOneLine(_sql)
    # print('_sql = ' + str(_sql))
    # 分离insert和select
    _insertSql, _selectSql = splitInsertAndSelect(_sql)
    # 有没有 insert 语句
    if _insertSql:
        _insertTable, _insertFields = insertToWhereAndWhat(_insertSql)
        _selectTableInfo["insertTable"] = str(_insertTable)
        _selectTableInfo["insertFields"] = _insertFields
    # 是不是join两个表
    _joinType, _joinTables = selectFromJoin(_selectSql)
    if _joinTables:
        # 是一个双表 join
        _selectFieldsA, _selectTableA = selectWhatFromWhere(_joinTables[0])
        _selectTableInfo["selectTableA"] = str(_selectTableA)
        _selectTableInfo["selectFieldsA"] = _selectFieldsA
        _selectFieldsB, _selectTableB = selectWhatFromWhere(_joinTables[1])
        _selectTableInfo["selectTableB"] = str(_selectTableB)
        _selectTableInfo["selectFieldsB"] = _selectFieldsB
    else:
        # 不是一个join的话
        _selectFields, _selectTable = selectWhatFromWhere(_selectSql)
        if _selectFields and _selectTableInfo:
            _selectTableInfo["selectTable"] = str(_selectTable)
            _selectTableInfo["selectFields"] = _selectFields
    return _selectTableInfo


# 将 insert 和 select 分离
def splitInsertAndSelect(sqlStr_: str):
    _insertReg = r'(?i)(insert into .+\)) (select .+)'
    _insertResult = re.search(_insertReg, sqlStr_)
    if _insertResult:
        return _insertResult.group(1), _insertResult.group(2)
    else:
        # 不是一个insert 语句，所以，直接把SQL当做一个select 传递回去
        return None, sqlStr_


# 获得向 哪个表 插入 哪些数据
def insertToWhereAndWhat(sqlStr_: str):
    _insertReg = r'(?i)insert into (.+)\((.+)\)'
    _insertResult = re.search(_insertReg, sqlStr_)
    if _insertResult:
        _where = _insertResult.group(1)
        _whatStr = _insertResult.group(2)
        _what = getRealFields(_whatStr)
        return _where, _what
    else:
        print("ERROR insertToWhereAndWhat : " + sqlStr_ + "\n 当前的正则无法匹配")
        return None, None


# 从join形式的语句中提取select
def selectFromJoin(sqlStr_: str):
    _joinReg = r'(?i)select (.*?) from \(*(.+)\)* as (\w+?) (left )*(right )*join \(*(.+)\)* as (\w+?) on (.+)'
    _joinResult = re.search(_joinReg, sqlStr_)
    _joinType = None
    if _joinResult:
        # join 模式，左还是右，或者是无
        if _joinResult.group(4):
            _joinType = "left"
        elif _joinResult.group(5):
            _joinType = "right"
        # join 的 两个 select
        _firstSelect = _joinResult.group(2)
        _secondSelect = _joinResult.group(6)
        _joinSelectReg = r'(?i)(.*) as (\w+) (left )*(right )*join \(*(.+)\)* as (\w+) on (.+)'
        _joinSelectResult = re.search(_joinSelectReg, sqlStr_)
        # 如果 select from 的目标就是一个表名而不是一个select的临时表
        if not _firstSelect.find("select") >= 0:
            # 第一个 select 为 as之前的部分
            return _joinType, [_joinSelectResult.group(1), _secondSelect]
        else:
            return _joinType, [_firstSelect, _secondSelect]
    else:
        return None, None


def selectWhatFromWhere(sqlStr_: str):
    _what = None
    _where = None
    _selectReg = r'(?i)select (.+) from (.+)'
    _selectResult = re.search(_selectReg, sqlStr_)
    if _selectResult:
        _what = _selectResult.group(1)
        _what = getRealFields(_what)
        _whereReg = r'(?i)(.+) where (.+)'
        _whereResult = re.search(_whereReg, _selectResult.group(2))
        # 如果有where条件
        if _whereResult:
            _where = _whereResult.group(1)
        else:
            _groupByReg = r'(?i)(.+) group by (.+)'
            _groupByResult = re.search(_groupByReg, _selectResult.group(2))
            # 如果有group条件
            if _groupByResult:
                _where = _groupByResult.group(1)
            else:
                # 没有 where 也没有 group ，那么就是表名
                _where = _selectResult.group(2)
    else:
        return None, None

    if _what and _where:
        return _what, _where
    else:
        print("ERROR selectWhatFromWhere : " + sqlStr_ + "\n 结果不正确")
        print('_what = ' + str(_what))
        print('_where = ' + str(_where))
        return None, None


def getRealFields(fieldStr_: str):
    _fields = utils.codeUtils.splitByChar(fieldStr_, ",")
    _fieldsSet = set()
    for _field in _fields:
        _field = _field.strip()
        print('_field = ' + str(_field))
        _treeDict = dict({})
        _treeDict["type"] = None
        _treeDict["subs"] = []
        _treeDict["code"] = _field
        # # 通用解析
        _treeDict = utils.codeUtils.analyseCode(_field)
        # 在语言中解析，递归的过程在 codeUtils 里面
        _treeDict = utils.codeUtils.subAnalyseInLan(_treeDict, analyseCodeInSql)
        # 递归节点，返回满足 type == var 的节点列表，这样取得的就是字段
        _treeNodeList = utils.codeUtils.recursiveTreeNodeToListByType(_treeDict, ["var"])
        # 字段名列表<取 . 分割后的最后一个，因为 join 的时候 select 表，使用了别名>
        _fieldList = [_treeNode["code"].split(".")[-1] for _treeNode in _treeNodeList]
        # 节点列表变成集合，集合相加来去重
        _fieldsSet = _fieldsSet.union(set(_fieldList))

    # 出重后的节点集合，变成列表返回
    return list(_fieldsSet)


'''
case when a.x*b > 0 and e != 25 then c else d end
          a.x*b > 0 and e != 25      c      d
          a.x*b > 0     e != 25
          a.x*b   0     e    25
          a.x b
          
case when a.x*b > 0 and e != 25 then c else d end <caseWhen>
          
not
!

and
&&
&

or
||
|

==
=

!=

>
<
>=
<=

'''


# 解析 在 sql 关键字下的代码
def analyseCodeInSql(code_: str):
    # 自己的节点信息
    _treeDictNode = dict({})
    _treeDictNode["subs"] = []
    _treeDictNode["code"] = code_
    # case when 判断
    _caseWhenReg = r'(?i)case when[ |\(](.*)[ \)]then[ |\(](.*)[ \)]else[ |\(](.*)[ \)]end'
    _caseWhenResult = re.search(_caseWhenReg, code_)
    _distinctReg = r'(?i)distinct (.*)'
    _distinctResult = re.search(_distinctReg, code_)
    _asReg = r'(?i)(.*) as (\w+)'
    _asResult = re.search(_asReg, code_)
    _isNullReg = r'(\w+) is null'
    _isNullResult = re.search(_isNullReg, code_)
    # 当一个字段和系统中的关键字相同的时候，这个时候，需要两侧加 ` 号。它还是一个变量
    _sysVarReg = r'`(\w+)`'
    _sysVarResult = re.search(_sysVarReg, code_)

    if _caseWhenResult:
        _treeDictNode["type"] = "caseWhen"
        _treeDictNode["subs"].append(utils.codeUtils.analyseCode(_caseWhenResult.group(2)))
        _treeDictNode["subs"].append(utils.codeUtils.analyseCode(_caseWhenResult.group(3)))
    elif _distinctResult:
        _treeDictNode["type"] = "distinct"
        _treeDictNode["subs"].append(utils.codeUtils.analyseCode(_distinctResult.group(1)))
    elif _isNullResult:
        _treeDictNode["type"] = "isNull"
        _treeDictNode["subs"].append(utils.codeUtils.analyseCode(_distinctResult.group(1)))
    elif _asResult:
        _treeDictNode["type"] = "as"
        _treeDictNode["subs"].append(utils.codeUtils.analyseCode(_asResult.group(1)))
    elif _sysVarResult:
        _treeDictNode["type"] = "var"
        _treeDictNode["code"] = _sysVarResult.group(1)
    else:
        _treeDictNode = utils.codeUtils.analyseCode(code_)
        if not _treeDictNode["type"]:
            raise utils.pyUtils.AppError("analyseCodeInSql 未能解析的字段 : " + _treeDictNode["code"])

    return _treeDictNode


def formatToDay():
    return


if __name__ == "__main__":
    _sql = """
insert into olap.OLAP_goldroom_D(
  log_date,
  sub_area_id,
  gold_room_type,
  help_gold_player_num,
  help_gold_num
)
select
  gen_date,
  sub_area_id,
  -1 as gold_room_type,
  count(DISTINCT player_id),
  ifnull(sum(gold),0)
from
  ods.player_gold_bill
where
  type=3003
  and
  gen_date= date '{date}'
GROUP BY
  gen_date,
  sub_area_id,
  gold_room_type,
  type
-- on DUPLICATE KEY UPDATE
--   help_gold_player_num=VALUES(help_gold_player_num),
--   help_gold_num=VALUES(help_gold_num)
    """
    _selectTableInfo = analyseSql(_sql)
    print('_selectTableInfo = \n' + str(json.dumps(_selectTableInfo, indent=4, sort_keys=False, ensure_ascii=False)))
