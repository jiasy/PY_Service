# !/usr/bin/env python3
# 数学 线性代数 统计学
from collections import Counter
from utils.math_linearAlgebra_vector import sum_of_squares, dot
import math
# from __future__ import division


# this isn't right if you don't from __future__ import division
def mean(x):
    return sum(x) / len(x)


# 中位数 : 数据中间点的值
def median(v):
    """finds the 'middle-most' value of v"""
    n = len(v)
    sorted_v = sorted(v)
    midpoint = n // 2

    if n % 2 == 1:
        # if odd, return the middle value
        return sorted_v[midpoint]
    else:
        # if even, return the average of the middle values
        lo = midpoint - 1
        hi = midpoint
        return (sorted_v[lo] + sorted_v[hi]) / 2


# 分位数 : 少于数据特定百分比的一个值
def quantile(x, p):
    """returns the pth-percentile value in x"""
    p_index = int(p * len(x))
    return sorted(x)[p_index]


# 概念众数 : 出现次数最多的一个或多个数
def mode(x):
    """returns a list, might be more than one mode"""
    counts = Counter(x)
    max_count = max(counts.values())
    return [x_i for x_i, count in counts.items()
            if count == max_count]


# 极差 : "range" 在python中是关键字，所以，这里换了一个名
def data_range(x):
    return max(x) - min(x)


# 平均值
def de_mean(x):
    """translate x by subtracting its mean (so the result has mean 0)"""
    x_bar = mean(x)
    return [x_i - x_bar for x_i in x]


# 方差 : 方差衡量了单个变 量对均值的偏离程度
def variance(x):
    """assumes x has at least two elements"""
    n = len(x)
    deviations = de_mean(x)
    return sum_of_squares(deviations) / (n - 1)


# 标准差 : 方差的开方
def standard_deviation(x):
    return math.sqrt(variance(x))


# 通过 25% - 75% 的分位数差，来规避 极差 可能出现的异常值问题
def interquartile_range(x):
    return quantile(x, 0.75) - quantile(x, 0.25)


# 协方差 : 协方差衡量了两个变量对均值的串联偏离程度
def covariance(x, y):
    n = len(x)
    return dot(de_mean(x), de_mean(y)) / (n - 1)


# 相关 : 协方差除以两个变量的标准差
def correlation(x, y):
    stdev_x = standard_deviation(x)
    stdev_y = standard_deviation(y)
    if stdev_x > 0 and stdev_y > 0:
        return covariance(x, y) / stdev_x / stdev_y
    else:
        return 0  # 如果没有变动，相关系数为零
