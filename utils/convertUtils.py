from decimal import Decimal

def strToInt(str_: str):
    return int(Decimal(str_))


def strToFloat(str_):
    return float(str_)


# 转换文字
def toStr(object_):
    if isinstance(object_, float) or isinstance(object_, int) or isinstance(object_, bool):
        return str(object_)
    elif isinstance(object_, str):
        return object_
    else:
        return None
