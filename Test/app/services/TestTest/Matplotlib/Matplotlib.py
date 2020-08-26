#!/usr/bin/env python3
import time
from base.supports.Base.BaseInService import BaseInService
from pyspark.streaming import StreamingContext
import os
from utils import pyUtils
from utils import strUtils
from matplotlib import pyplot as plt
from collections import Counter
import numpy as np
import math
import seaborn


class Matplotlib(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(Matplotlib, self).create()

    def destory(self):
        super(Matplotlib, self).destory()

    def doTest(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")

        # 绘画 二维函数
        x = np.linspace(0, 5, 50)
        y = np.linspace(0, 5, 50)[:, np.newaxis]
        z = np.sin(x) ** 10 + np.cos(10 + y * x) * np.cos(x)
        plt.imshow(z, origin='lower', extent=[0, 5, 0, 5], cmap='viridis')
        plt.colorbar()
        plt.show()

        # 设置绘图风格
        seaborn.set()
        # 简单的线图 -------------------------------------------------------------------------
        years = [1950, 1960, 1970, 1980, 1990, 2000, 2010]
        gdp = [300.2, 543.3, 1075.9, 2862.5, 5979.6, 10289.7, 14958.3]

        # 创建一幅线图，x轴是年份， y轴是gdp
        plt.plot(years, gdp, color='green', marker='o', linestyle='solid')

        # 添加一个标题
        plt.title("title")

        # 给y轴加标记
        plt.ylabel("ylabel")
        plt.show()

        # 条形图  ---------------------------------------------------------------------------
        movies = ["Annie Hall", "Ben-Hur", "Casablanca", "Gandhi", "West Side Story"]
        num_oscars = [5, 11, 3, 8, 10]
        # 条形的默认宽度是0.8，因此我们对左侧坐标加上0.1
        #  这样每个条形就被放置在中心了
        xs = [i + 0.1 for i, _ in enumerate(movies)]
        #  使用左侧x坐标[xs]和高度[num_oscars]画条形图
        plt.bar(xs, num_oscars)
        plt.ylabel("ylabel")
        plt.title("title")
        # 使用电影的名字标记x轴，位置在x轴上条形的中心
        plt.xticks([i + 0.5 for i, _ in enumerate(movies)], movies)
        plt.show()

        # 为直方图使用条形图 ------------------------------------------------------------------
        grades = [83, 95, 91, 87, 70, 0, 85, 82, 100, 67, 73, 77, 0]
        decile = lambda grade: grade // 10 * 10
        histogram = Counter(decile(grade) for grade in grades)

        plt.bar(
            [x for x in histogram.keys()],  # 每个条形向左侧移动4个单位
            histogram.values(),  # 给每个条形设置正确的高度
            8)  # 每个条形的宽度设置为8

        plt.axis([-5, 105, 0, 5])

        plt.xticks([10 * i for i in range(11)])  # x轴标记为0，10， ...，100
        plt.xlabel("xlabel-scoreGroup")
        plt.ylabel("ylabel-studentCount")
        plt.title("考试分数分布图")
        plt.show()

        # 条形图  ---------------------------------------------------------------------------
        mentions = [500, 505]
        years = [2013, 2014]
        _barWidth = 0.1
        # 条状设置
        plt.bar(years, mentions, _barWidth)
        # x 坐标
        plt.xticks(years)
        # y轴描述
        plt.ylabel("ylabel")
        # x,y 轴 的范围
        plt.axis([2012.5, 2014.5, 0, 550])
        # 标题
        plt.title("title")
        # 显示
        plt.show()

        # 线图 -----------------------------------------------------------------------------
        variance = [1, 2, 4, 8, 16, 32, 64, 128, 256]
        bias_squared = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        total_error = [x + y for x, y in zip(variance, bias_squared)]
        xs = [i for i, _ in enumerate(variance)]

        # 可以多次调用plt.plot
        # 以便在同一个图上显示多个序列
        plt.plot(xs, variance, 'g-', label='variance')  # 绿色实线
        plt.plot(xs, bias_squared, 'r-.', label='bias^2')  # 红色点虚线
        plt.plot(xs, total_error, 'b:', label='total error')  # 蓝色点线

        # 因为已经对每个序列都指派了标记
        # 所以可以自由地布置图例
        # loc=9指的是“顶部中央”
        plt.legend(loc=9)
        plt.xlabel("模型复杂度")
        plt.title("偏差 - 方差权衡图")
        plt.show()

        # 朋友数与花在网站上的分钟数之间的关系散点图 --------------------------------------------
        friends = [70, 65, 72, 63, 71, 64, 60, 64, 67]
        minutes = [175, 170, 205, 120, 220, 130, 105, 145, 190]
        labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

        plt.scatter(friends, minutes)

        # 每个点加标记
        for label, friend_count, minute_count in zip(labels, friends, minutes):
            plt.annotate(
                label,
                xy=(friend_count, minute_count),  # 把标记放在对应的点上
                xytext=(5, -5),  # 但要有轻微偏离
                textcoords='offset points'
            )
        plt.title("日分钟数与朋友数")
        plt.xlabel("朋友数")
        plt.ylabel("花在网站上的日分钟数")
        plt.show()

        # 带有可比较的轴的同一个散点图 -------------------------------------------------------
        test_1_grades = [99, 90, 85, 97, 80]
        test_2_grades = [100, 85, 60, 90, 70]

        plt.scatter(test_1_grades, test_2_grades)
        plt.title("Axes Aren't Comparable")
        plt.xlabel("测验1的分数")
        plt.ylabel("测验2的分数")
        plt.axis("equal")  # x,y 轴刻度长相等。这样可以方便比较
        plt.show()

        # 个数汇总直方图 ------------------------------------------------------------------
        num_friends = [100, 49, 41, 40, 25, 11, 23, 4, 56, 88, 97, 6, 55, 44, 12,
                       32, 15, 14, 12, 15, 2, 3, 5, 8, 33, 42, 34]

        # 最大，最小值
        largest_value = max(num_friends)
        smallest_value = min(num_friends)
        # 排序后，取最大最小值，第几个大的值
        sorted_values = sorted(num_friends)
        smallest_value = sorted_values[0]
        second_smallest_value = sorted_values[1]
        second_largest_value = sorted_values[-2]

        # 1 # 1 # 49
        friend_counts = Counter(num_friends)
        xs = range(101)
        ys = [friend_counts[x] for x in xs]
        plt.bar(xs, ys)
        plt.axis([0, 101, 0, 25])
        plt.title("朋友数的直方图")
        plt.xlabel("朋友个数")
        plt.ylabel("人数")
        plt.show()

        # 随机的话 在正太分布内随机 ---------------------------------------------------------
        # 正太分布图，随机多少个分几次
        data = np.random.randn(1, 40000)
        # 将随机得到的二维数组，转换成一维数组
        dataList = data.flatten().tolist()
        # 然后，将随机得到的数*100 再取整
        dataList = [math.floor(_data * 100) for _data in dataList]
        # 取得每一个值的个数
        dataListCount = Counter(dataList)
        # x 轴 的范围，从数组中的 最小值 到 最大值
        xs = range(min(dataList), max(dataList))
        # y 轴 是每一个值的出现次数
        ys = [dataListCount[x] for x in xs]
        # plt.plot(xs, ys, 'g-', label='variance')  # 绿色实线
        # plt.scatter(xs, ys)
        plt.bar(xs, ys)
        # 按照正太分布随机，实际上就是随机数出现的个数是正态分布
        plt.show()

        # 身高数据显示
        heightStr = "189 170 189 163 183 171 185 168 173 183 173 173 175 178 183 193 178 173 174 183 183 168 170 178 182 180 183 178 182 188 175 179 183 193 182 183 177 185 188 188 182 185"
        heights = [int(_str) for _str in heightStr.split(" ")]
        heightsArr = np.array(heights)
        # 每五个值合并成一个坐标点，成直方图<连续>
        plt.hist(heightsArr)
        plt.title('Height Distribution of US Presidents')
        plt.xlabel('height (cm)')
        plt.ylabel('number')
        plt.show()
        # 每一个数值作为一个坐标点，成直方图<不连续>
        _heightCounter = Counter(heightsArr)
        xs = range(min(heightsArr), max(heightsArr))
        ys = [_heightCounter[x] for x in xs]
        plt.bar(xs, ys)
        plt.show()

