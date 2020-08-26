# !/usr/bin/env python3
# 递归将 jsonPathA_ 的内容 覆盖到 jsonPathB_ 的内容上，中保存到 jsonPathC_ 中
# 如果 jsonPathC_ 没传,则保存到 jsonPathB_ 中
import json
import utils.fileUtils


# jsonDict 的内容合并
def mergeAToB(jsonDictA_, jsonDictB_):
    for _key in jsonDictA_:
        if type(jsonDictA_[_key]) == dict and jsonDictB_.has_key(_key) and type(jsonDictB_[_key]) == dict:
            mergeAToB(jsonDictA_[_key], jsonDictB_[_key])
        else:
            jsonDictB_[_key] = jsonDictA_[_key]
    return jsonDictB_


# jsonA_的内容会覆盖jsonB_的内容,然后保存在 jsonPathC_ 路径中
def jsonMerge(jsonPathA_, jsonPathB_, jsonPathC_=None):
    _jsonDictA = utils.fileUtils.dictFromJsonFile(jsonPathA_)
    _jsonDictB = utils.fileUtils.dictFromJsonFile(jsonPathB_)
    _jsonDictB = mergeData(_jsonDictA, _jsonDictB)

    # 获取写入的路径
    _targetPath = None
    if jsonPathC_:
        _targetPath = jsonPathC_
    else:
        _targetPath = jsonPathB_

    # 实际写入过程
    utils.fileUtils.writeFileWithStr(
        _targetPath,
        str(
            json.dumps(
                _jsonDictB,
                indent=4,
                sort_keys=False,
                ensure_ascii=False
            )
        )
    )


# 修改json文件内容
def changeJsonContent(jsonPath_, writeDict_):
    _jsonDict = utils.fileUtils.dictFromJsonFile(jsonPath_)
    mergeAToB(writeDict_, _jsonDict)
    _jsonStr = str(json.dumps(_jsonDict, indent=4, sort_keys=False, ensure_ascii=False))
    utils.fileUtils.writeFileWithStr(jsonPath_, _jsonStr)
