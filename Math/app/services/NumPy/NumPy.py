#!/usr/bin/env python3
from base.supports.Service.BaseService import BaseService
from utils import *
import numpy as np


class NumPy(BaseService):
    def __init__(self, sm_):
        super().__init__(sm_)
        print("NumPy version : " + np.__version__)

    def create(self):
        super(NumPy, self).create()

        # np 和 python 原生的关系
        self.sample_relation_with_python()

        # np 数组 和 python list 的比较
        self.sample_compare_with_python()

        # 创建 数组
        self.sample_create_array()

        # 数组的属性
        # 确定数组的大小、形状、存储大小、数据类型。
        self.sample_array_operate_property()

        # 数组的索引
        # 获取和设置数组各个元素的值。
        self.sample_array_operate_index()

        # 数组的切分
        # 在大的数组中获取或设置更小的子数组。
        self.sample_array_operate_slice()

        # 数组的变形
        # 改变给定数组的形状。
        self.sample_array_operate_transform()

        # 数组的拼接和分裂
        # 将多个数组合并为一个，以及将一个数组分裂成多个。
        self.sample_array_operate_join_split()

        # 通用函数
        self.sample_UFuncs()

        # 数组转置
        self.sample_arr_transpose()

        # 聚合
        self.sample_aggregation()

        # 广播
        self.sample_broadcast()

    def destory(self):
        super(NumPy, self).destory()

    # np 和 python 原生的关系
    def sample_relation_with_python(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")

        pyList = [3.14, 2, 3, 4]
        npArray = np.array(pyList, dtype='float32')
        print('npArray = ' + str(npArray))
        npArray2 = np.array([range(i, i + 3) for i in [2, 4, 6]])
        print('npArray2 = \n' + str(npArray2))

    # 和python原生进行比较
    def sample_compare_with_python(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")

        print("np 创建 100万 长度 数组")
        with pyUtils.TimeIt() as _timeit:
            my_arr = np.arange(1000000)
        print("list 创建 100 万 长度 数组")
        with pyUtils.TimeIt() as _timeit:
            my_list = list(range(1000000))

        print("np 100万 长度 数组 每个元素*2")
        with pyUtils.TimeIt() as _timeit:
            my_arr2 = my_arr * 2
        print("list 100万 长度 数组 每个元素*2")
        with pyUtils.TimeIt() as _timeit:
            my_list2 = [x * 2 for x in my_list]

    # 创建 数组
    def sample_create_array(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        '''
        np 的 数据类型 < dtype >
            bool_            布尔值（真、 True 或假、 False ），用一个字节存储 
            int_             默认整型（类似于 C 语言中的 long ，通常情况下是 int64 或 int32 ） 
            intc             同 C 语言的 int 相同（通常是 int32 或 int64 ） 
            intp             用作索引的整型（和 C 语言的 ssize_t 相同，通常情况下是 int32 或 int64 ）
            int8       i1    字节（byte，范围从 –128 到 127） 
            int16      i2    整型（范围从 –32768 到 32767）
            int32      i4    整型（范围从 –2147483648 到 2147483647） 
            int64      i8    整型（范围从 –9223372036854775808 到 9223372036854775807） 
            uint8      u1    无符号整型（范围从 0 到 255） 
            uint16     u2    无符号整型（范围从 0 到 65535） 
            uint32     u4    无符号整型（范围从 0 到 4294967295）
            uint64     u8    无符号整型（范围从 0 到 18446744073709551615）
            float_     f8/d  float64 的简化形式 
            float16    f2    半精度浮点型：符号比特位， 5 比特位指数（exponent）， 10 比特位尾数（mantissa）
            float32    f4/f  单精度浮点型：符号比特位， 8 比特位指数， 23 比特位尾数 
            float64    f8/d  双精度浮点型：符号比特位， 11 比特位指数， 52 比特位尾数 
            complex_   c16   complex128 的简化形式 
            complex64  c8    复数，由两个 32 位浮点数表示 
            complex128 c16   复数，由两个 64 位浮点数表示
            object     O     Python对象类型
            string_    S     固定长度的字符串类型，例如，长度为10的字符串，应使用S10
            unicode_   U     固定长度的uicode类型(字节数由平台决定)。如: U10
        '''

        # 创建一个长度为10的数组，数组的值都是0
        npZeros = np.zeros(10, dtype=int)
        print('npZeros = \n' + str(npZeros))

        # 创建一个3×5的浮点型数组，数组的值都是1
        npOnes = np.ones((3, 5), dtype=float)
        print('npOnes = \n' + str(npOnes))

        # 创建一个3×5的浮点型数组，数组的值都是3.14
        npFull = np.full((3, 5), 3.14)
        print('npFull = \n' + str(npFull))

        # 创建一个线性序列
        #  从0开始，到20结束，步长为2。左闭右开区间 [)
        #  (它和内置的 range() 函数类似)
        npArange = np.arange(0, 20, 2)
        print('npArange = \n' + str(npArange))

        # 创建一个5个元素的数组，这5个数均匀地分配到0~1
        npLineSpace = np.linspace(0, 1, 5)
        print('npLineSpace = \n' + str(npLineSpace))

        # 创建一个3×3的、在0~1均匀分布的随机数组成的数组
        np3x3 = np.random.random((3, 3))
        print('np3x3 = \n' + str(np3x3))

        # 创建一个3×3的、均值为0、方差为1的
        #  正态分布的随机数数组
        npNormalDistribution = np.random.normal(0, 1, (3, 3))
        print('npNormalDistribution = \n' + str(npNormalDistribution))

        # 创建一个3×3的、[0, 10)区间的随机整型数组
        npRandomInt = np.random.randint(0, 10, (3, 3))
        print('npRandomInt = \n' + str(npRandomInt))

        # 创建一个3×3的单位矩阵
        npEye = np.eye(3)
        print('npEye = \n' + str(npEye))

        # 创建一个由3个整型数组成的未初始化的数组
        #  数组的值是内存空间中的任意值
        npEmpty = np.empty(3)
        print('npEmpty = \n' + str(npEmpty))

    # 数组的属性
    def sample_array_operate_property(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        # 设置随机数种子，确保每次随机结果一致。
        np.random.seed(0)
        # 一维数组
        x1 = np.random.randint(10, size=6)
        # 二维数组
        x2 = np.random.randint(10, size=(3, 4))
        # 三维数组
        x3 = np.random.randint(10, size=(3, 4, 5))
        print('x1 = \n' + str(x1))
        print('x2 = \n' + str(x2))
        print('x3 = \n' + str(x3))
        print("x3 ndim: ", x3.ndim)  # 数组的维度
        print("x3 shape:", x3.shape)  # 数组每个维度的大小
        print("x3 size: ", x3.size)  # 数组的总大小 个数
        print("x3 dtype:", x3.dtype)  # 数组的数据类型
        print("x3 itemsize:", x3.itemsize, "bytes")  # 数据的字节大小 每一个大小
        print("x3 nbytes:", x3.nbytes, "bytes")  # nbytes 跟 itemsize 和 size 的乘积大小相等

    # 数组的索引
    def sample_array_operate_index(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        # 设置随机数种子，确保每次随机结果一致。
        np.random.seed(0)
        # 一维数组
        x1 = np.random.randint(10, size=6)
        # 二维数组
        x2 = np.random.randint(10, size=(3, 4))
        print('x1 = \n' + str(x1))
        print('x1[0] = ' + str(x1[0]))
        print('x1[-1] = ' + str(x1[-1]))
        print('x2 = \n' + str(x2))
        print('x2[0,1] = ' + str(x2[0, 1]))
        print('x2[-1,-2] = ' + str(x2[-1, -2]))
        x2[0, 0] = 1
        # NumPy 数组是固定类型的，试图将一个浮点 值插入一个整型数组时，浮点值会被截短成整型。
        x2[0, 1] = 3.14
        print('x2 = \n' + str(x2))
        # 布尔型索引 -------------------------------------------------------------
        names = np.array(['Bob', 'Joe', 'Will', 'Bob', 'Will', 'Joe', 'Joe'])
        # 28 个元素，分成7行，每行4个元素
        dataList = np.arange(1, 29, 1).reshape((7, 4))
        print('dataList = \n' + str(dataList))
        # 当 names 对应元素为 Bob 时，相应 dataList 对应的行保留下来
        dataFilter = dataList[(names == "Bob") | (names == "Will")]
        print('dataFilter = \n' + str(dataFilter))
        dataFilter = dataList[~(names == "Bob")]
        print('dataFilter = \n' + str(dataFilter))
        dataFilter = dataList[dataList > 15]
        print('dataFilter = \n' + str(dataFilter))
        dataList[dataList > 15] = 0
        print('dataList = \n' + str(dataList))
        # 花式索引 数组作为索引id传入索引位置
        arr = np.arange(0, 32).reshape((8, 4))
        print('arr[[0]] = ' + str(arr[[0]]))  # arr[0]
        print('arr[[2, 0]] = \n' + str(arr[[2, 0]]))  # arr[2] arr[0]
        print('arr[[0, 2][3, 1]] = ' + str(arr[[0, 2], [3, 1]]))  # a[0,3] a[2,1]
        # arr1 = arr[[1, 5, 7, 2]]
        # arr1[:,[0,3,1,2]] 行全取，然后每一行顺序调整
        print('arr[[1, 5, 7, 2]][:, [0, 3, 1, 2]] = \n' + str(arr[[1, 5, 7, 2]][:, [0, 3, 1, 2]]))

    # 数组的切分
    def sample_array_operate_slice(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        # x[start:stop:step]
        # 一维数组
        x = np.arange(10)
        print('x[:5] = ' + str(x[:5]))  # 前五个元素
        print('x[5:] = ' + str(x[5:]))  # 索引五之后的元素
        print('x[4:7] = ' + str(x[4:7]))  # 中间的子数组
        print('x[::2] = ' + str(x[::2]))  # 每隔一个元素
        print('x[1::2] = ' + str(x[1::2]))  # 每隔一个元素，从索引1开始
        # 当步长为负数的时候，可以理解成 start 参数和 stop 参数默认是被交换的
        print('x[::-1] = ' + str(x[::-1]))  # 所有元素，逆序的
        print('x[5::-2] = ' + str(x[5::-2]))  # 从索引5开始每隔一个元素逆序
        # 多维子数组
        np.random.seed(0)
        x2 = np.random.randint(10, size=(3, 4))
        print('x2 = \n' + str(x2))
        print('x2[:2, :3] = \n' + str(x2[:2, :3]))  # 两行，三列
        print('x2[:3, ::2] = \n' + str(x2[:3, ::2]))  # 所有行，每隔一列
        print('x2[::-1, ::-1] = \n' + str(x2[::-1, ::-1]))  # 子数组维度也可以同时被逆序
        # 获取数组的行和列
        print('x2[:, 0] = ' + str(x2[:, 0]))  # 获取 第一 列
        print('x2[0, :] = ' + str(x2[0, :]))  # 获取 第一 行 等价于 x2[0]
        # 抽取的是子视图，而不是副本，所以，修改这个子视图，就是在修改这个数组
        x2_sub = x2[:2, :2]
        print('x2_sub = \n' + str(x2_sub))  # 前两行，前两列 的视图
        # 要创建数组的副本，使用copy()方法
        x2_sub_copy = x2_sub.copy()
        print('x2_sub_copy = \n' + str(x2_sub_copy))
        # 两个数组是否值一致
        if x2_sub.all() == x2_sub_copy.all():
            print("x2_sub and x2_sub_copy value are all the same")
        # 两个对象的地址不一致
        if not id(x2_sub) == id(x2_sub_copy):
            print("x2_sub and x2_sub_copy are not the same one")

    # 数组的变形
    def sample_array_operate_transform(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        # 一位数组变二维数组，reshape数组维度变形
        arr_3x3 = np.arange(1, 10).reshape((3, 3))
        print('arr_3x3 = \n' + str(arr_3x3))
        # 获取 第一行
        arr_1x3 = arr_3x3[:1, :]
        print('arr_1x3 = \n' + str(arr_1x3))
        # 获取 第一列
        arr_3x1 = arr_3x3[:, :1]
        print('arr_3x1 = \n' + str(arr_3x1))

        arr_3 = np.array([1, 2, 3])
        print('arr_3 = \n' + str(arr_3))
        # 通过newaxis获得的行向量
        arr_1x3_newaxis = arr_3[np.newaxis, :]
        print('arr_1x3_newaxis = \n' + str(arr_1x3_newaxis))
        # 通过newaxis获得列向量
        arr_3x1_newaxis = arr_3[:, np.newaxis]
        print('arr_3x1_newaxis = \n' + str(arr_3x1_newaxis))

    # 数组的拼接和分裂
    def sample_array_operate_join_split(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        # 拼接 ---------------------
        x = np.array([1, 2, 3])
        y = np.array([3, 2, 1])
        z = [99, 99, 99]
        print('np.concatenate([x, y]) = ' + str(np.concatenate([x, y])))
        print('np.concatenate([x, y, z]) = ' + str(np.concatenate([x, y, z])))

        grid = np.array([[1, 2, 3], [4, 5, 6]])
        print('grid = \n' + str(grid))
        # 沿着第一个轴拼接
        print('np.concatenate([grid, grid]) = \n' + str(np.concatenate([grid, grid])))
        # 沿着第二个轴拼接，索引从 0 开始的
        print('np.concatenate([grid, grid], axis=1) = \n' + str(np.concatenate([grid, grid], axis=1)))

        # 垂直栈 拼接
        print('np.vstack([x, grid]) = \n' + str(np.vstack([x, grid])))
        y = np.array([[99], [99]])
        print('y = \n' + str(y))
        # 水平栈 拼接
        print('np.hstack([grid, y]) = \n' + str(np.hstack([grid, y])))

        # 分裂 ---------------------
        x = [1, 2, 3, 99, 99, 3, 2, 1]
        # 索引列表记录的是分裂点位置
        x1, x2, x3 = np.split(x, [3, 5])
        print(x1, x2, x3)
        # 水平，竖直 分裂
        grid = np.arange(16).reshape((4, 4))
        print('grid = \n' + str(grid))
        upper, lower = np.vsplit(grid, [2])
        print('upper = \n' + str(upper))
        print('lower = \n' + str(lower))
        left, right = np.hsplit(grid, [2])
        print('left = \n' + str(left))
        print('right = \n' + str(right))

    # 通用函数
    def sample_UFuncs(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        # 两个数组，对应的每一项相除
        print('np.arange(5) / np.arange(1, 6) = ' + str(np.arange(5) / np.arange(1, 6)))
        # 二维数组，每一项乘方
        x1 = np.arange(9)
        print('np.sqrt(x1) = ' + str(np.sqrt(x1)))
        print('np.exp(x1) = ' + str(np.exp(x1)))
        x2 = x1.reshape((3, 3))
        print('x2 ** 2 = \n' + str(x2 ** 2))

        '''
            运算符号 调用的通用函数 功能描述
            +     np.add          加法运算(即1+1=2)
            -     np.subtract     减法运算(即3-2=1)
            -     np.negative     负数运算(即-2)
            *     np.multiply     乘法运算(即2*3=6)
            /     np.divide       除法运算(即3/2=1.5)
            //    np.floor_divide 地板除法运算(ﬂoor，division，即3//2=1)
            **    np.power        指数运算(即2**3=8)
            %     np.mod          模/余数(即9%4=1)
        '''

        # 绝对值
        x = np.array([-2, -1, 0, 1, 2])
        abs(x)
        # 三角函数 ,从零到PI，创建三个元素
        theta = np.linspace(0, np.pi, 3)
        print("theta = ", theta)
        print("sin(theta) = ", np.sin(theta))
        print("cos(theta) = ", np.cos(theta))
        print("tan(theta) = ", np.tan(theta))

        x = [-1, 0, 1]
        print("x = ", x)
        print("arcsin(x) = ", np.arcsin(x))
        print("arccos(x) = ", np.arccos(x))
        print("arctan(x) = ", np.arctan(x))

        x = np.random.randn(8)
        y = np.random.randn(8)
        xy_max = np.maximum(x, y)  # 取每一位的最大值
        remainder, whole_part = np.modf(xy_max)  # 整数 小数 按照每一位 分离
        print('remainder = \n' + str(remainder))
        print('whole_part = \n' + str(whole_part))
        print('np.sqrt(xy_max) = \n' + str(np.sqrt(xy_max ** 2)))
        # scipy.special 专用的通用函数，包含了你需要的计算函数

        # 指定输出
        x = np.arange(5)
        print('x = ' + str(x))
        y = np.empty(5)
        print('y = ' + str(y))
        print('np.multiply(x, 10, out=y) = \n' + str(np.multiply(x, 10, out=y)))
        # 5个元素计算的结果，放入10个元素的数组中，每间隔一个元素放入一个
        y = np.zeros(10)
        np.multiply(x, 10, out=y[::2])
        print('y = \n' + str(y))

        # 聚合，直接出结果
        x = np.arange(1, 6)
        print('np.add.reduce(x) = ' + str(np.add.reduce(x)))
        print('np.multiply.reduce(x) = ' + str(np.multiply.reduce(x)))
        # 聚合，存储每次计算的中间结果
        print('np.add.accumulate(x) = ' + str(np.add.accumulate(x)))
        print('np.multiply.accumulate(x) = ' + str(np.multiply.accumulate(x)))
        # 外积
        print('np.multiply.outer(x, x) = \n' + str(np.multiply.outer(x, x)))

    # 数组转置
    def sample_arr_transpose(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        _rowCount = 4
        _colCount = 3
        _indexArr = np.arange(0, _rowCount * _colCount).reshape(_rowCount, _colCount)
        print('_indexArr = \n' + str(_indexArr))
        print('_indexArr.T = \n' + str(_indexArr.T))
        print('np.dot(_indexArr,_indexArr.T) = \n' + str(np.dot(_indexArr, _indexArr.T)))

    # 聚合
    def sample_aggregation(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        L = np.random.random(100)
        print('np.sum(L) = ' + str(np.sum(L)))
        print('np.min(L) = ' + str(np.min(L)))
        print('np.max(L) = ' + str(np.max(L)))

        M = np.random.random((3, 4))
        print('M = \n' + str(M))
        print('M.sum() = ' + str(M.sum()))
        print('M.min(axis=0) = ' + str(M.min(axis=0)))  # 第一轴 聚合
        print('M.max(axis=1) = ' + str(M.max(axis=1)))  # 第二轴 聚合

        '''
            np.sum          np.nansum                 计算元素的和
            np.prod         np.nanprod                计算元素的积
            np.mean         np.nanmean                计算元素的平均值
            np.std          np.nanstd                 计算元素的标准差
            np.var          np.nanvar                 计算元素的方差
            np.min          np.nanmin                 找出最小值
            np.max          np.nanmax                 找出最大值
            np.argmin       np.nanargmin              找出最小值的索引
            np.argmax       np.nanargmax              找出最大值的索引
            np.median       np.nanmedian              计算元素的中位数
            np.percentile   np.nanpercentile          计算基于元素排序的统计值
            np.any          N/A                       验证任何一个元素是否为真
            np.all          N/A                       验证所有元素是否为真
        '''
        heightStr = "189 170 189 163 183 171 185 168 173 183 173 173 175 178 183 193 178 173 174 183 183 168 170 178 182 180 183 178 182 188 175 179 183 193 182 183 177 185 188 188 182 185"
        heights = [int(_str) for _str in heightStr.split(" ")]
        heightsArr = np.array(heights)
        print("heightsArr.mean() : ", heightsArr.mean())  # 平均值
        print("heightsArr.std() : ", heightsArr.std())  # 均方差
        print("heightsArr.min() : ", heightsArr.min())  # 最小值
        print("heightsArr.max() : ", heightsArr.max())  # 最大值
        print('np.percentile(heights, 25) = ' + str(np.percentile(heightsArr, 25)))
        print('np.median(heights) = ' + str(np.median(heightsArr)))  # 中位数
        print('np.percentile(heights, 75) = ' + str(np.percentile(heightsArr, 75)))

    # 广播 <按照规则，将操作拓展到每一个元素>
    def sample_broadcast(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + " ------------------ -")
        a = np.arange(3)[np.newaxis, :]
        b = np.arange(3)[:, np.newaxis]
        print('a = ' + str(a))
        print('b = \n' + str(b))
        print('a + b = \n' + str(a + b))
        # 归一化 normalization --------------------------------------------
        X = np.random.random((10, 3))
        print('X = \n' + str(X))
        X_mean = X.mean()
        print('X_mean = \n' + str(X_mean))
        # 归一化 结果
        X_centered = X - X_mean
        print('X_centered = \n' + str(X_centered))
        # 归一化 的结果 它的平均值 为 零
        print('X_centered.mean() = ' + str(X_centered.mean()))


