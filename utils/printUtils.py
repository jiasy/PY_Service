# !/usr/bin/env python3
# 
def printPropertys(object_):
    print("propertys : " + str(object_.__dict__))


def printList(list_: list, prefix_: str = ""):
    _length: int = len(list_)
    for _idx in range(_length):
        print(prefix_ + str(_idx) + ' : ' + str(str(list_[_idx])))
