# !/usr/bin/env python3
# 数学 线性代数 矢量
import math
from functools import reduce


#
# functions for working with vectors
#
# 矢量加法，这里的矢量，v,w 可能是多维矢量
def vector_add(v, w):
    """adds two vectors componentwise"""
    return [v_i + w_i for v_i, w_i in zip(v, w)]


# 矢量减法
def vector_subtract(v, w):
    """subtracts two vectors componentwise"""
    return [v_i - w_i for v_i, w_i in zip(v, w)]


# 矢量数组值求和
def vector_sum(vectors):
    return reduce(vector_add, vectors)


# 标量乘法(向量的每个元素乘以一个数)
def scalar_multiply(c, v):
    return [c * v_i for v_i in v]


# 均值
def vector_mean(vectors):
    """compute the vector whose i-th element is the mean of the
    i-th elements of the input vectors"""
    n = len(vectors)
    return scalar_multiply(1 / n, vector_sum(vectors))


# 点乘(表示对应元素的分量乘积之和)
def dot(v, w):
    """v_1 * w_1 + ... + v_n * w_n"""
    return sum(v_i * w_i for v_i, w_i in zip(v, w))


# 平方和
def sum_of_squares(v):
    """v_1 * v_1 + ... + v_n * v_n"""
    return dot(v, v)


# 向量的 大小
def magnitude(v):
    return math.sqrt(sum_of_squares(v))


def squared_distance(v, w):
    return sum_of_squares(vector_subtract(v, w))


# 两个向量的距离
def distance(v, w):
    return magnitude(squared_distance(v, w))
