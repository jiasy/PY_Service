# !/usr/bin/env python3


# 两个Dict合并
def mergeDict(dict_a_, dict_b_):
    # 第二个字典展开，加入第一个字典形成的新字典。
    return dict(dict_a_, **dict_b_)


# 显示字典结构 < 字符串中不能有\n >
def showDictStructure(object_, depth_: int = 0):
    # 只有在第一层，才会可能出现有list,之后的层级，都是先遍历取得第一项目
    if isinstance(object_, list) or isinstance(object_, tuple):
        print("|      " * depth_ + "+-- [0]")
        showDictStructure(object_[0], depth_ + 1)
    elif isinstance(object_, dict):
        for _key, _value in object_.items():
            if isinstance(_value, dict):
                print("|      " * depth_ + "+--" + str(_key))
                showDictStructure(_value, depth_ + 1)
            elif isinstance(_value, list) or isinstance(object_, tuple):
                if len(_value) > 0:
                    print("|      " * depth_ + "+--" + str(_key) + " [0]")
                    showDictStructure(_value[0], depth_ + 1)
                else:
                    print("|      " * depth_ + "+--" + str(_key) + " []")
            else:
                print("|      " * depth_ + "+--" + str(_key))
    elif isinstance(object_, str):
        print("|      " * depth_ + "- <str>")
    elif isinstance(object_, bool):
        print("|      " * depth_ + "- <bool>")
    elif isinstance(object_, int):
        print("|      " * depth_ + "- <int>")
    elif isinstance(object_, float):
        print("|      " * depth_ + "- <float>")
    elif isinstance(object_, complex):
        print("|      " * depth_ + "- <complex>")
    else:
        print("Unkown type")

