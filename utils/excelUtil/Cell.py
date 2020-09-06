# !/usr/bin/env python3
from utils import convertUtils


class Cell(object):
    def __init__(self, value_, col_, row_, pos_):
        self.value = None
        self.strValue = None
        # 赋值
        self.write(value_)
        self.col = col_
        self.row = row_
        self.pos = pos_
        pass

    def __str__(self):
        return 'cell %s:%s p:%s v:%s' % (
            str(self.col).rjust(3), str(self.row).ljust(3), self.pos.ljust(5), self.strValue
        )

    def write(self, value_):
        self.value = value_
        self.strValue = convertUtils.toStr(self.value)
