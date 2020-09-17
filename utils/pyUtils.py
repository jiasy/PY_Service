#!/usr/bin/env python3
from functools import wraps
import threading
import importlib
import inspect
import time
import cProfile
import sys
import math

'''
    # 获取 字符串内语句执行时的执行状况，并保存成一个文本文件
    cProfile.run('1+2', 'my_math.profile')
    
    # 读取这个执行状况的文本文件，进行输出
    p = pstats.Stats('my_math.profile')
    p.strip_dirs().sort_stats(-1).print_stats()  # strip_dirs:从所有模块名中去掉无关的路径信息
    p.strip_dirs().sort_stats("name").print_stats()  # sort_stats():把打印信息按照标准的module/name/line字符串进行排序
    p.strip_dirs().sort_stats("cumulative").print_stats(3)  # print_stats():打印出所有分析信息
'''


# 根据包路径创建类的实例对象
def getObjectByClassPath(classPath_, *args):
    _modelPath, _className = classPath_.rsplit(".", 1)
    _model = importlib.import_module(_modelPath)
    _object = getattr(_model, _className)(*args)  # 反射并实例化 *args 元组拆包
    return _object


# 获取这个方法所在的当前方法的名称runServiceByJsonDict
def getCurrentRunningFunctionName():
    return inspect.stack()[1][3]


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class AppError(Exception):
    def __init__(self, value):
        self.value = "【ERROR】" + value
        print(self.value)
        sys.exit(1)

    def __str__(self):
        return repr(self.value)


# 装饰器 测量 fn 函数的执行实现。对方法的计时
'''
    from utils.pyUtils import timefn
    @timefn
    def func(parameters):
        # do_something
    
    #直接执行即可，装饰器会自动记录用时
    func("参数") 
'''


def timeit(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
        t1 = time.time() * 1000
        result = fn(*args, **kwargs)
        t2 = time.time() * 1000
        _funcName = fn.__name__
        _timeDiff = str(t2 - t1)
        print("timefn : " + _funcName + " took " + _timeDiff + " ms")
        return result

    return measure_time


# with 方式，对代码段进行计时，用上下文管理器计时
'''
    from utils.pyUtils import TimeIt
    with TimeIt() as _timeit:
        print ('do other things')
'''


class TimeIt(object):
    def __enter__(self):
        self.t0 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('timefn : {time} ms'.format(time=(math.floor((time.time() - self.t0) * 1000))))
