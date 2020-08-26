#!/usr/bin/env python3
import os

from base.supports.Service.BaseService import BaseService

from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, Row

from utils import pyUtils
from utils import fileUtils
from utils import resUtils
import json
from utils import pyUtils
from sqlalchemy.engine import create_engine
import pandas as pd
import pandas.io.sql as sql


class SparkTest(BaseService):

    def __init__(self, sm_):
        super().__init__(sm_)
        self.testJsonFilePath = fileUtils.getPath(self.resPath, "testJsonStr.json")
        self.conf: SparkConf = None
        self.sc: SparkContext = None
        self.spark: SparkSession = None
        self.sqlCtx: SQLContext = None
        # self.writeJsonToResPath()
        self.initSpark()

    def writeJsonToResPath(self):
        self.testJsonStr = '{"result":1245186,"roomCardCount":1000000,"battleId":0,"roomId":0,"marqueeVersion":{"low":1,"high":0,"unsigned":false},"newMail":null,"newLimitedCostlessActivity":false,"noticeVersion":{"low":0,"high":0,"unsigned":false},"activityInfo":[{"id":300001,"startTime":{"low":-576284416,"high":345,"unsigned":false},"endTime":{"low":-72284416,"high":345,"unsigned":false}},{"id":300005,"startTime":{"low":-224153600,"high":349,"unsigned":false},"endTime":{"low":438245400,"high":350,"unsigned":false}},{"id":300008,"startTime":{"low":-2140022784,"high":353,"unsigned":false},"endTime":{"low":-238493672,"high":133356,"unsigned":false}},{"id":300004,"startTime":{"low":-1994684416,"high":345,"unsigned":false},"endTime":{"low":-1908285416,"high":345,"unsigned":false}},{"id":300002,"startTime":{"low":131409920,"high":355,"unsigned":false},"endTime":{"low":217808920,"high":355,"unsigned":false}},{"id":300007,"startTime":{"low":-2140022784,"high":353,"unsigned":false},"endTime":{"low":-584823784,"high":353,"unsigned":false}},{"id":300000,"startTime":{"low":-576284416,"high":345,"unsigned":false},"endTime":{"low":46435072,"high":368,"unsigned":false}}],"buttonValue":13,"timeStamp":{"low":1316055502,"high":355,"unsigned":false},"clubId":null,"createTime":{"low":1037369829,"high":355,"unsigned":false},"connGroup":"c74d97b01eae257e44aa9d5bade97baf","isIdentityVerify":false,"isAgency":false,"agtWebUrl":"","combatId":0,"area":10002,"displayId":5198814,"mttStartTime":{"low":0,"high":0,"unsigned":false},"ticket":0,"phone":"","notifyRedDot":[],"pushRegisterId":""}'
        fileUtils.writeFileWithStr(self.testJsonFilePath, self.testJsonStr)

    def initSpark(self):
        # 集群 URL : local 这个特殊值可以让 Spark 运行在单机单线程上而无需连接到集群
        _clusterType = "local"
        # 应用名 : appName 当连接到一个集群时，这个值可以帮助你在集群管理器的用户界面中找到你的应用。
        _appName = self.app.appName
        self.conf = SparkConf().setMaster(_clusterType).setAppName(_appName)
        self.sc = SparkContext(conf=self.conf)
        self.spark = SparkSession \
            .builder \
            .appName("Python Spark SQL basic example") \
            .config("spark.some.config.option", "some-value") \
            .getOrCreate()
        self.sqlCtx = SQLContext(self.sc)
        global blankLines
        blankLines = self.sc.accumulator(0)

    def create(self):
        super(SparkTest, self).create()
        # self.test_parallelize()
        # _testTextRDD = self.test_textFile()
        # self.test_RDD(_testTextRDD)
        # self.test_map()
        # self.test_flatMap()
        # self.test_createPairRDD()
        # self.test_aggregate()
        self.test_jsonStrToDataFrame()
        # self.test_jsonFileWrite()
        # self.test_sparkSql()
        # self.test_createSchema()
        # self.test_accumulator()
        # self.test_sparkStreaming()
        # self.test_presto()

    def destory(self):
        super(SparkTest, self).destory()

    def test_parallelize(self):
        # 一个区内进行RDD转化
        self.sc.parallelize(["pandas", "i like pandas"])
        # 分成两个区
        self.sc.parallelize([1, 2, 3, 4], 2)

    def test_textFile(self):
        _testTextFilePath = fileUtils.getPath(self.app.resPath, "README.md")
        # Spark 的 RDD 包含两种操作
        _testTextRDD = self.sc.textFile(_testTextFilePath)
        return _testTextRDD

    def test_RDD(self, targetRDD_):
        # 向Spark传递函数
        def pythonInLine(line_):
            # 确保 filter 中没有 self 之类的引用，否者，引用会被序列化，传递给Spark的成本增加。
            return "Python" in line_

        # 转化操作 （transformation）
        _pythonInLineRDD = targetRDD_.filter(pythonInLine)
        _starInLineRDD = targetRDD_.filter(lambda line: "* " in line)
        # 返回包含两个RDD所有元素的新RDD，可能有重复元素
        _unionRDD = _pythonInLineRDD.union(_starInLineRDD)
        # 去重
        _unionRDD = _unionRDD.distinct()
        # 让 Spark 把这个 RDD 缓存吗，cache() 与使用默认存储级别调用 persist() 是一样的。
        _unionRDD.cache()
        # 行动操作（action）: Spark 只会 惰性 计算这些 RDD
        # 每当我们调用一个新的行动操作时，整个 RDD 都会从头开始计算
        # 只有第一次在一个行动操作中用到时，才会真正计算 (count 和 first 都是 action)
        _count = _unionRDD.count()
        self.app.info.log("_count = " + str(_count))
        _first = _unionRDD.first()
        # print("_first = " + str(_first))
        _take5 = _unionRDD.take(5)  # 取5条
        # print("_take5 = " + str(_take5))
        _all = _unionRDD.collect()  # 取所有<注意数据大小，别给内存弄爆了>

        # 返回两个RDD都中都有的元素组成的RDD
        _intersectionRDD = _pythonInLineRDD.intersection(_starInLineRDD)
        _same = _intersectionRDD.collect()

    # RDD 每一个元素处理之后，获得新的 RDD
    def test_map(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _numsRDD = self.sc.parallelize([1, 2, 3, 4])
        # map() 接收一个函数， 把这个函数用于 RDD 中的每个元素， 将函数的返回结果作为结果
        _squaredRDD = _numsRDD.map(lambda x: x * x)
        # 输出每一个元素，平方数
        for _num in _squaredRDD.collect():
            print("%i " % _num)

    # RDD 每一个元素处理之后，变成多个元素，然后再将所有元素构成新的 RDD
    def test_flatMap(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _lines = self.sc.parallelize(["hello world", "hi"])
        # flatMap 得到了一个由各列表中的元素组成的 RDD， 而不是一个由列表组成的 RDD
        _words = _lines.flatMap(lambda line: line.split(" ")).collect()
        for _word in _words:
            print("%s " % _word)
        # 读取json文件，返回一个二元组(文件路径,文件内容)
        _jsonRDD = self.sc.wholeTextFiles(self.testJsonFilePath)

        # 读取每一行json信息，将二元组的第二项，作为字符串解析成Json对象，将其中的 activityInfo 作为新 RDD 的元素。
        def _getActivityInfoFunc(jsonInfoKV_):
            _jsonValue = jsonInfoKV_[1]
            _activityInfoDict = json.loads(_jsonValue)["activityInfo"]
            return _activityInfoDict

        _json_activityInfo_RDD = _jsonRDD.flatMap(lambda _jsonInfoKV: (_getActivityInfoFunc(_jsonInfoKV)))
        # 去重
        _json_activityInfo_RDD.distinct()
        # RDD 转 DF
        _json_activityInfo_DF = self.spark.createDataFrame(_json_activityInfo_RDD)
        # 创建临时表
        _json_activityInfo_DF.registerTempTable("activityInfo")
        _resultsRDD = self.sqlCtx.sql(
            "SELECT startTime.low,endTime.low FROM activityInfo WHERE id = 300001L")

        for _result in _resultsRDD.collect():
            print("_result = " + str(_result))

    # 创建 Pair RDD
    def test_createPairRDD(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _lines = self.sc.parallelize(["key1 value1", "key2 value2", "key2 value22", "key3 value3"])
        # 转换成键值对儿
        _pairs = _lines.map(lambda _item: (_item.split(" ")[0], _item.split(" ")[1]))
        # 值字符串长6以内的保留
        _pairs = _pairs.filter(lambda _keyValue: len(_keyValue[1]) <= 6)
        # 输出满足条件的每一个键值
        for (_key, _value) in _pairs.collect():
            print(str(_key) + " = " + str(_value))

    def test_aggregate(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        # 统计单词出现的次数
        _lines = self.sc.parallelize(["hello value1", "hello value2", "hi value22", "fuck value3"])
        # 获取每个词 ["hello","value1","hello","value2","hi","value22","fuck","value3"]
        _words = _lines.flatMap(lambda _line: _line.split(" "))
        # 每个词变成（词，1）元组(pairRDD)
        _wordAndOnes = _words.map(lambda _word: (_word, 1)).cache()
        # pairRDD 二元组，第一元做Key,第二元做值
        _wordReduce = _wordAndOnes.reduceByKey(lambda _valueReduce, _valueNext: _valueReduce + _valueNext)
        # 输出 次 和个数
        for _key, _value in _wordReduce.collect():
            print(str(_key) + " = " + str(_value))

        # aggregate 的方法计算 单词出现次数
        _wordAgg = _wordAndOnes.aggregateByKey(
            0,  # 初始值
            (lambda _valueReduce, _valueNext: _valueReduce + _valueNext),  # RDD 中的元素合并起来放入累加器
            (lambda _reduce, reduceNext: _reduce + reduceNext)  # 累加器两两合并
        )
        # 输出 次 和个数
        for _key, _value in _wordAgg.collect():
            print(str(_key) + " = " + str(_value))

        # 计算平均值
        _numsRDD = self.sc.parallelize([1, 2, 3, 4])
        _sumInfo = _numsRDD.aggregate(
            (0, 0),  # 初始值(累加值,计数)
            (lambda _sumReduce, _value: (_sumReduce[0] + _value, _sumReduce[1] + 1)),  # 将每一个value进行累加，计数器累计
            (lambda _sumReduceReduce, _sumReduceNext: (
                _sumReduceReduce[0] + _sumReduceNext[0], _sumReduceReduce[1] + _sumReduceNext[1]))  # 累加器再一次合并
        )
        _average = _sumInfo[0] / float(_sumInfo[1])
        print("_average = " + str(_average))

    def test_jsonStrToDataFrame(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _jsonDataFrame = self.spark.read.json(self.testJsonFilePath)
        _jsonDataFrame.printSchema()
        _jsonDataFrame.show()
        _activityInfo = _jsonDataFrame.selectExpr("activityInfo")
        _activityInfo.show()

    def test_jsonFileWrite(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        # 写入文件的路径
        _writeToPath = fileUtils.getPath(self.app.resPath, "activityInfo.json")
        # 产生一个元组列表 (文件路径,文件内容)
        jsonRDD = self.sc.wholeTextFiles(self.testJsonFilePath)
        for _jsonKeyValue in jsonRDD.collect():
            print("_jsonKeyValue = " + str(_jsonKeyValue))
        # 元组列表的每一项，取其中的 文件内容，转换成 json字典对象，构成新的RDD
        # 字典对象RDD，过滤，将包含键的元素，构成新的RDD
        # 将元素中的字段取出，构成新的RDD
        jsonDataFilter = jsonRDD \
            .map(lambda _jsonKeyValue: json.loads(_jsonKeyValue[1])) \
            .filter(lambda _jsonDict: _jsonDict["activityInfo"]) \
            .map(lambda _jsonDict: _jsonDict["activityInfo"])
        # activityInfo 字段内容构成的RDD
        for _jsonDataFilter in jsonDataFilter.collect():
            print("_jsonDataFilter = " + str(_jsonDataFilter))
        # 如果，没有写过的话，就写一份
        if not os.path.exists(_writeToPath):
            jsonDataFilter.saveAsTextFile(_writeToPath)

    #
    def test_sparkSql(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _tweets = self.sqlCtx.read.json(self.testJsonFilePath)
        _tweets.printSchema()
        _tweets.show()
        _tweets.registerTempTable("tempTable")
        # 即便过滤出来的某一个属性，其查询的结构也是一样的。都需要从activityInfo这个顶层属性开始做字段查找。
        # _activityInfo = _tweets.selectExpr("activityInfo")
        # _activityInfo.show()
        # _activityInfo.registerTempTable("tempTable")
        _resultsRDD = self.sqlCtx.sql(
            "SELECT activityInfo.startTime.low,activityInfo.endTime.low FROM tempTable")
        for _result in _resultsRDD.collect():
            print("_result = " + str(_result))

    def test_createSchema(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        # 数据
        _jsonDatas = [{'a': 'aaa', 'b': 'bbb', 'c': 'ccc'},
                      {'a': 'aaaa', 'b': 'bbbb', 'c': 'cccc', 'd': 'dddd', 'e': 'eeee'}]
        _jsonDatas = [json.dumps(_jsonDict) for _jsonDict in _jsonDatas]

        # 已知结构
        schema = ['a', 'b', 'c', 'd']
        fields = [StructField(_fieldName, StringType(), True) for _fieldName in schema]
        schema = StructType(fields)

        rdd = self.sc.parallelize(_jsonDatas)
        # 已知 结构 会被保留，未知结构会被抛弃
        df = self.sqlCtx.read.schema(schema).json(rdd)
        for data in df.collect():
            print("data = " + str(data))
        df.registerTempTable("tempTable")
        _resultsRDD = self.sqlCtx.sql("SELECT c,d FROM tempTable")
        for _result in _resultsRDD.collect():
            print("_result = " + str(_result))

    def test_accumulator(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")

        def accumulatorFunc():
            global blankLines
            blankLines += 1

        for i in range(10):
            accumulatorFunc()

        global blankLines
        print("blankLines = " + str(blankLines))

    def test_sparkStreaming(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        self.getSubClassObject("SparkStreaming")
        self.getSubClassObject("Kafka")
        # self.showCurrentBaseObejctsInfo()
        self.sparkStreaming.destory()
        self.kafka.destory()
        # self.showCurrentBaseObejctsInfo()

    def test_presto(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        self.getSubClassObject("Presto")
        self.presto.doTest()
        self.presto.destory()
