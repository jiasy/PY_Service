# !/usr/bin/env python3

import re
import json

import utils.strUtils


def splitCodeAndOneLineComment(line_: str, oneLineComment_: str, codeLeft_: str = None):
    # 单行注释
    _commonMatch = re.search(oneLineComment_, line_)
    _code = line_
    _comment = ""
    # 满足当行注释的时候
    if _commonMatch:
        _code = _commonMatch.group(1)
        if codeLeft_:
            _code = _code + codeLeft_
        _comment = _commonMatch.group(2)
        # 取注释之外的部分，判断字符串
        _singleQuotesCount = utils.strUtils.charCount(_code, "\'")

        # 前半部分，单引号为基数，那么这个注释，就不是注释
        if not _singleQuotesCount % 2 == 0:
            # 要从后后半部分中继续寻找注释
            _code, _commentFromRight = splitCodeAndOneLineComment(_comment, oneLineComment_, line_.split(_comment)[0])
            _comment = _commentFromRight
            return _code, _comment
        else:
            # 双引号为基数，那么这个注释，就不是注释
            _doubleQuotesCount = utils.strUtils.charCount(_commonMatch.group(1), '"')
            if not _doubleQuotesCount % 2 == 0:
                # 要从后后半部分中继续寻找注释
                _code, _commentFromRight = splitCodeAndOneLineComment(_comment, oneLineComment_, _code)
                _comment = _commentFromRight
                return _code, _comment
    if codeLeft_:
        return codeLeft_ + _code, _comment
    else:
        return _code, _comment


# 字符加括号，变成字符空格加括号
def addSpaceInCharBracket(code_: str):
    _code = code_
    # 括号相邻添加空格间隔
    _k1Reg = r'(\w)(\()'
    _k2Reg = r'(\()(\w)'
    for _k1 in re.findall(_k1Reg, _code):
        _code = _code.replace(_k1[0] + _k1[1], _k1[0] + " " + _k1[1])
    for _k2 in re.findall(_k2Reg, _code):
        _code = _code.replace(_k2[0] + _k2[1], _k2[0] + " " + _k2[1])
    return _code


# 字符空格加括号的组合，变成字符加括号
def removeSpaceInCharBracket(code_: str):
    _code = code_
    # 括号相邻添加空格间隔
    _k1Reg = r'(\w)(\s+)(\()'
    _k2Reg = r'(\()(\s+)(\w)'
    for _k1 in re.findall(_k1Reg, _code):
        _code = _code.replace(_k1[0] + _k1[1] + _k1[2], _k1[0] + _k1[2])
    for _k2 in re.findall(_k2Reg, _code):
        _code = _code.replace(_k2[0] + _k2[1] + _k2[2], _k2[0] + _k2[2])
    return _code


'''
字符串分组，树形结构向下延伸
(func1(a,b,c+d)*func2('func3(x)',12)+func4([1,e,(f+1)%2]))
 func1(a,b,c+d) func2('func3(x)',12) func4([1,e,(f+1)%2]
       a,b,c+d        'func3(x)' 12        [1,e,(f+1)%2]
           c d                              1,e,(f+1)%2
                                            1 e (f+1) 2
                                                 f+1
                                                 f 1
(func1(a,b,c+d)*func2('func3(x)',12)+func4([1,e,(f+1)%2])) <()>
 func1(a,b,c+d)*func2('func3(x)',12)+func4([1,e,(f+1)%2])  <+>
 func1(a,b,c+d) ------------------------------------------ <func>
       a | | |                                             <var>
         b | |                                             <var>
           c+d                                             <+>
           c |                                             <var>
             d                                             <var>
                func2('func3(x)',12) --------------------- <func>
                      'func3(x)',12                        <,>
                      'func3(x)' |                         <str>
                                 12                        <number>
                                     func4([1,e,(f+1)%2])  <func>
                                           [1,e,(f+1)%2]   <[]>
                                            1,e,(f+1)%2    <,>
                                            1 |            <number>
                                              e            <var>
                                                (f+1)%2    <%>
                                                (f+1) |    <()>
                                                 f+1  |    <+>
                                                 f |  |    <var>
                                                   1  |    <number>
                                                      2    <number>
           
'''


def doSplitCode(code_: str, splitList_: list, dictNode_: dict):
    for _splitChar in splitList_:
        # 尝试分割
        _splitArr = splitByChar(code_, _splitChar)
        # 发生过分割
        if len(_splitArr) > 1:
            # 记录分割使用的字符
            dictNode_["type"] = _splitChar
            for _splitStr in _splitArr:
                if not _splitStr.strip() == "":
                    # 发生过分割，分割的每个部分自行再继续处理
                    dictNode_["subs"].append(analyseCode(_splitStr))
                # else:
                #     print('code_ = ' + str(code_))
                #     print('_splitStr = ' + str(_splitStr))
            return True
    return False


# 获取括号内的内容，第一个遇到的 括号，引号 为当前使用的分割符号
def analyseCode(code_: str):
    # 自己的节点信息
    _treeDictNode = dict({})
    # 括号字符相临时，去除中间的空格，然后去掉两侧空格
    _code = removeSpaceInCharBracket(code_).strip()
    # 保存原始字符串,去两侧空格
    _treeDictNode["code"] = _code
    _treeDictNode["type"] = None
    _treeDictNode["subs"] = []
    # 各种符号的计数
    _yuanBracketCount: int = 0
    _fangBracketCount: int = 0
    _daBracketCount: int = 0
    _singleQuotes: bool = False
    _doubleQuotes: bool = False
    _currentSplitStart: str = None
    _currentSplitEnd: str = None
    _twoSideSplitStartIdx: int = 0
    # 是否是括号类，如果括号终结了，后面还有其他的符号分割的话。后面会修改这个 type 值，先给一个默认值
    if _code[0] == "(":
        _treeDictNode["type"] = "()"
    elif _code[0] == "[":
        _treeDictNode["type"] = "[]"
    elif _code[0] == "{":
        _treeDictNode["type"] = "{}"
    elif _code[0] == "'" or _code[0] == '"':
        _treeDictNode["type"] = "str"
    elif utils.strUtils.is_number(_code):
        _treeDictNode["type"] = "number"
    elif re.match(r'^[a-zA-Z0-9_\.\-]+$', _code):
        # 从开始到结束只有字母数字下划线逗号，那么这个就是变量
        _treeDictNode["type"] = "var"
    elif re.match(r'^\w+\((.+)\)$', _code):
        # 字母加括号起始，括号结束
        _treeDictNode["type"] = "func"

    # 分割优先级，+ 一定 在 - 号前面，因为 - 可能只是一个标示负数的符号
    if not doSplitCode(code_, [",", "+", "-", "*", "/", "%"], _treeDictNode):  # 没有发生过逗号分割
        # 挨个字符遍历
        for _idx, _char in enumerate(code_):
            # 两侧包括的部分，分割
            if _char == "(":
                _yuanBracketCount = _yuanBracketCount + 1
            elif _char == "[":
                _fangBracketCount = _fangBracketCount + 1
            elif _char == "{":
                _daBracketCount = _daBracketCount + 1
            elif _char == ")":
                _yuanBracketCount = _yuanBracketCount - 1
            elif _char == "]":
                _fangBracketCount = _fangBracketCount - 1
            elif _char == "}":
                _daBracketCount = _daBracketCount - 1
            elif _char == '"':
                _doubleQuotes = not _doubleQuotes
            elif _char == "'":
                _singleQuotes = not _singleQuotes

            # 可分割部分
            if not _doubleQuotes and not _singleQuotes and _yuanBracketCount == 0 and _fangBracketCount == 0 and _daBracketCount == 0:
                # 包含部分结束<强制优先级>
                if _char == _currentSplitEnd:
                    _codeSub = code_[_twoSideSplitStartIdx + 1:_idx]
                    # 是括号类的继续向下分割
                    if not (_currentSplitStart == '"' or _currentSplitStart == "'"):
                        _treeDictNode["subs"].append(analyseCode(_codeSub))
                    # 结束切分
                    _currentSplitStart = None
                    _currentSplitEnd = None

            if not _currentSplitStart:
                if _char == "(":
                    _currentSplitStart = "("
                    _currentSplitEnd = ")"
                elif _char == "[":
                    _currentSplitStart = "["
                    _currentSplitEnd = "]"
                elif _char == "{":
                    _currentSplitStart = "{"
                    _currentSplitEnd = "}"
                elif _char == '"':
                    _currentSplitStart = '"'
                    _currentSplitEnd = '"'
                elif _char == "'":
                    _currentSplitStart = "'"
                    _currentSplitEnd = "'"
                if _currentSplitStart:
                    _twoSideSplitStartIdx = _idx

    # 各种符号的计数
    assert _yuanBracketCount == 0, "圆括号没有收尾"
    assert _fangBracketCount == 0, "方括号没有收尾"
    assert _daBracketCount == 0, "大括号没有收尾"
    assert not _singleQuotes, "单引号没有收尾"
    assert not _doubleQuotes, "双引号没有收尾"
    if _treeDictNode["type"] == None:
        assert False, "配有匹配到类型 code : " + code_ + " type : " + str(_treeDictNode["type"])

    return _treeDictNode


# 通用中无法解析的代码，放到代码类型中提供的特殊解析，进行进步一的操作
def subAnalyseInLan(treeDictNode_: dict, languageAnalyse_):
    _treeDictNode = treeDictNode_
    # 不是通用的就重新在具体的语言中确认自己的类型
    if not _treeDictNode["type"]:
        _treeDictNode = languageAnalyse_(_treeDictNode["code"])
    # 解析出新的子对象，然后，每一个子对象，再在具体语言中解析一次
    _newSubs = []
    for _sub in _treeDictNode["subs"]:
        _newSubs.append(subAnalyseInLan(_sub, languageAnalyse_))
    _treeDictNode["subs"] = _newSubs
    return _treeDictNode


# 通过 char 来分割 字符串，当中的各种括号自行匹配
def splitByChar(code_: str, spChar_: str):
    _yuanBracketCount: int = 0
    _fangBracketCount: int = 0
    _daBracketCount: int = 0
    _singleQuotes: bool = False
    _doubleQuotes: bool = False
    _lastStartCharIdx: int = 0
    _splitArr: list = []
    # 去掉空格
    _code = code_.strip()
    _codeLength = len(_code)

    # 挨个字符遍历
    for _idx, _char in enumerate(_code):
        if _char == "(":
            _yuanBracketCount = _yuanBracketCount + 1
        elif _char == "[":
            _fangBracketCount = _fangBracketCount + 1
        elif _char == "{":
            _daBracketCount = _daBracketCount + 1
        elif _char == ")":
            _yuanBracketCount = _yuanBracketCount - 1
        elif _char == "]":
            _fangBracketCount = _fangBracketCount - 1
        elif _char == "}":
            _daBracketCount = _daBracketCount - 1
        elif _char == '"':
            _doubleQuotes = not _doubleQuotes
        elif _char == "'":
            _singleQuotes = not _singleQuotes
        elif _char == spChar_:
            if not _doubleQuotes and not _singleQuotes and _yuanBracketCount == 0 and _fangBracketCount == 0 and _daBracketCount == 0:
                # 第一个 字符就是分割符 且为逗号的才会添加一个空。如果是 - 有可能就是表示这个数是负数，从而不需要分割
                if not _idx == 0 or not spChar_ == "-":
                    if _idx == 0:
                        _splitArr.append("")
                    else:
                        _splitStr = _code[_lastStartCharIdx:_idx]
                        _splitArr.append(_splitStr)
                    _lastStartCharIdx = _idx + 1

    # 最后一组在循环外添加，也就是说，无论如何都至少有一个元素
    _splitStr = _code[_lastStartCharIdx:_codeLength]
    _splitArr.append(_splitStr)

    return _splitArr


# 降符合条件的 type 条件的节点，构成列表
def recursiveTreeNodeToListByType(treeNodeDict_: dict, filters_: list, finalList_: list = None):
    # 外部调用的时候不用传递数组，自己创建一个
    _finalList = finalList_
    _isMainBoo = False
    if not _finalList:
        _isMainBoo = True
        _finalList = []
        if treeNodeDict_["type"] in filters_:
            _finalList.append(treeNodeDict_)
    # 在subs下循环
    for _sub in treeNodeDict_["subs"]:
        if _sub["type"] in filters_:
            _finalList.append(_sub)
        recursiveTreeNodeToListByType(_sub, filters_, _finalList)
    # 返回第一层调用时，创建的数组
    if _isMainBoo:
        return _finalList


# 去除 code_ 中的代码注释，comStr_ 为单行注释，multiComStr_ 为多行注释
# codeUtils.removeComment("/*当前行就结束的多行注释*/有效代码")
def removeComment(langType_: str, code_: str):
    _oneLineComRe = ""
    _multiLineComReBegin = ""
    _multiLineComInOneLine = ""
    _multiLineComReEnd = ""

    if langType_ == "js":
        _oneLineComRe = r'(.*)//(.*)'  # 不是向前匹配的，但是结果正确
        _multiLineComReBegin = r'(.*)/\*.*'
        _multiLineComInOneLine = r'(.*)/\*.*\*/(.*)'
        _multiLineComReEnd = r'.*\*/(.*)'
    elif langType_ == 'swift':
        _oneLineComRe = r'(.*)//(.*)'
        _multiLineComReBegin = r'(.*)/\*.*'
        _multiLineComInOneLine = r'(.*)/\*.*\*/(.*)'
        _multiLineComReEnd = r'.*\*/(.*)'
    elif langType_ == "sql":
        _oneLineComRe = r'(.*?)--(.*)'  # 向前匹配
        _multiLineComReBegin = r'(.*)/\*.*'
        _multiLineComInOneLine = r'(.*)/\*.*\*/(.*)'
        _multiLineComReEnd = r'.*\*/(.*)'
    else:
        print("ERROR langType_ is unexpected")

    # 是否处于多行注释中
    _multiCommon = False
    # 记录判断修改后的行
    _codeFinals = []
    # 读每一行
    _codes = code_.split('\n')
    # 行数
    _currentLine = 0
    # 逐行循环
    for _i in range(len(_codes)):
        _line = _codes[_i]
        # 记录行数
        _currentLine = _currentLine + 1
        # 临时的行副本
        _tempLine = _line.rstrip()

        # 处于多行注释,相当于代码是空行
        if _multiCommon:
            _tempLine = ''
            _codeFinals.append(_tempLine)
            continue

        # 多行注释/*...
        if _multiCommon == False:
            _commonMatchBegin = re.search(_multiLineComReBegin, _line)
            if _commonMatchBegin:
                _commonMatchOneLine = re.search(_multiLineComInOneLine, _line)
                if _commonMatchOneLine:
                    _multiCommon = False
                    # 多行注释在一行结束的时候，代码只能从前或者后取得
                    if _commonMatchOneLine.lastindex == 2 and not _commonMatchOneLine.group(2).strip() == '':
                        _tempLine = _commonMatchOneLine.group(2)
                    else:
                        _tempLine = _commonMatchOneLine.group(1)
                else:
                    _multiCommon = True
                    _tempLine = _commonMatchBegin.group(1)
        else:
            _commonMatchEnd = re.search(_multiLineComReEnd, _line)
            if _commonMatchEnd:
                _multiCommon = False
                _tempLine = _commonMatchEnd.group(1)

        _tempLine, _comment = splitCodeAndOneLineComment(_tempLine, _oneLineComRe, None)

        # 去掉空白行
        if _tempLine.strip() == '':
            _codeFinals.append('')
            continue

        _codeFinals.append(_tempLine)

    _codeWithOutCommentList = [_line for _line in _codeFinals if not _line == '']
    return '\n'.join(_codeWithOutCommentList)


if __name__ == "__main__":
    # _codeStr = '''
    # //单行注释
    # a//注释
    # '//注释'
    # "//注释"//注释
    # /*一行结束*/当行结束多行注释前
    # 当行结束多行注释后/*一行结束*/
    # b/*
    # 一行没结束
    # */
    # '''
    # for _idx, _line in list(enumerate(removeComment("js", _codeStr))):
    #     print('_idx,_line = ' + str(_idx) + "," + str(_line))

    #     _sqlStr = '''
    # CREATE TABLE if not exists olap.OLAP_goldroom_D (
    #   `log_date` date,--date NOT NULL,
    #   `sub_area_id` bigint,--int(11) NOT NULL,
    #   `gold_room_type` bigint,--int(11) NOT NULL,
    #   `gold_room_count` bigint,--int(11) DEFAULT NULL,
    #   `applied_player_num` bigint,--int(11) DEFAULT NULL, -- 报名人数
    #   `entre_player_num` bigint,--int(11) DEFAULT NULL, -- 参赛人数
    #   `entre_player_count` bigint,--int(11) DEFAULT NULL, -- 参赛人次
    #   `total_round` bigint,--int(11) DEFAULT NULL, -- 局数
    #   `average_round_secound` bigint,--int(11) DEFAULT NULL, -- 每局平均时长
    #   `gold_used_difference` bigint,--int(11) DEFAULT NULL, -- 金币场净消耗金币
    #   `gold_applied_num` bigint,--int(11) DEFAULT NULL, -- 服务费
    #   `mulit_entry_pay` bigint,--int(11) DEFAULT NULL, -- 多入口系统支出金币数
    #   `system_total_pay` bigint,--int(11) DEFAULT NULL, -- 金币不足系统支出金币数
    #   `help_gold_player_num` bigint,--int(11) DEFAULT NULL, -- 救济金人数
    #   `help_gold_num` bigint,--int(11) DEFAULT NULL, -- 救济金金币数
    #   -- `login_gold_player_num` bigint,--int(11) DEFAULT NULL,
    #   -- `login_gold_num` bigint,--int(11) DEFAULT NULL,
    #   -- `card_to_gold_player_num` bigint,--int(11) DEFAULT NULL,
    #   -- `card_to_gold_goldnum` bigint,--int(11) DEFAULT NULL,
    #   -- `card_to_gold_cardnum` bigint,--int(11) DEFAULT NULL,
    #   `new_player_entre_num` bigint,--int(11) DEFAULT NULL,  -- 新增中参加金币场人数
    #   -- `retention` bigint,--int(11) DEFAULT NULL,
    #   `active_player_total_gold` bigint,--int(11) DEFAULT NULL,  -- 活跃玩家剩余金币数
    #   `give_points` bigint,--int(11) DEFAULT NULL, -- 赠送点券数
    #   `high_power_service` bigint,--int(11) DEFAULT NULL, -- 高倍抽水服务费
    #   -- `big_win_share_gold` bigint,--int(11) DEFAULT NULL,
    #   -- `big_win_share_num` bigint,--int(11) DEFAULT NULL,
    #   `win_gold` bigint,--int(11) DEFAULT NULL, -- 赢金币数
    #   `lose_gold` bigint,--int(11) DEFAULT NULL, -- 输金币数
    #   `win_round` bigint,--int(11) DEFAULT NULL,  -- 赢人局数
    #   `lose_round` bigint,--int(11) DEFAULT NULL,  -- 输人局数
    #   `win_avg_gold` bigint,--int(11) DEFAULT NULL, -- 平均赢金币数
    #   `lose_avg_gold` bigint,--int(11) DEFAULT NULL, -- 平均输金币数
    #   `rate_winning` string,--varchar(20) DEFAULT NULL, -- 胜率
    #   `only_gold_player` bigint,--int(11) DEFAULT NULL, -- 只玩金币场玩家数
    #   -- `gold_total_without_play` bigint,--int(11) DEFAULT NULL,
    #   -- `gold_get_without_play` bigint,--int(11) DEFAULT NULL,
    #   -- `gold_cost_without_play` bigint,--int(11) DEFAULT NULL,
    #   -- `goldbean_to_gold_goldnum` bigint,--int(11) DEFAULT NULL,
    #   -- `match_reward` bigint,--int(11) DEFAULT NULL,
    #   -- x `public_get` bigint,--int(11) DEFAULT NULL,
    #   -- `new_player_get_gold` bigint,--int(11) DEFAULT NULL,
    #   -- x `activity_get_gold` bigint,--int(11) DEFAULT NULL,
    #   -- x `challenge_get_gold` bigint,--int(11) DEFAULT NULL,
    #   -- x `routine_task_get_gold` bigint,--int(11) DEFAULT NULL,
    #   -- `open_gift_get_gold` bigint,--int(11) DEFAULT NULL,
    #   -- x `other_public_get` bigint,--int(11) DEFAULT NULL,
    #   -- `goldless_exchange` bigint,--int(11) DEFAULT NULL,
    #   -- `change_luck_gift` bigint,--int(11) DEFAULT NULL,
    #   -- `uplevel_gift` bigint,--int(11) DEFAULT NULL,
    #   `guess_chicken_cost_gold` bigint,--int(11) DEFAULT NULL, -- 猜鸡押注金币
    #   `guess_chicken_win_gold` bigint,--int(11) DEFAULT NULL, -- 猜鸡赢金币
    #   -- PRIMARY KEY (`log_date`,`sub_area_id`,`gold_room_type`)
    # )
    #     '''
    #
    #     for _idx, _line in list(enumerate(removeComment("sql", _sqlStr))):
    #         print('_idx,_line = ' + str(_idx) + "," + str(_line))

    _info = analyseCode("(func1(a,b,c+d)*func2('func3(x)',12)+func4([1,e,(f+1)%2]))")
    print('_info = ' + str(json.dumps(_info, indent=4, sort_keys=False, ensure_ascii=False)))
    # analyseCode("ifnull(sum(gold), 0)")
    # analyseCode("ifnull('sum(gold)', 0)")

    # print(
    #     '0-sum(system_pay) = ' + str(
    #         json.dumps(
    #             analyseCode("0-sum(system_pay)"),
    #             indent=4,
    #             sort_keys=False,
    #             ensure_ascii=False
    #         )
    #     )
    # )
