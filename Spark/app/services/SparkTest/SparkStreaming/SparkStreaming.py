#!/usr/bin/env python3
import time
from base.supports.Base.BaseInService import BaseInService
from pyspark.streaming import StreamingContext
import os
from utils import pyUtils
from utils import strUtils


class SparkStreaming(BaseInService):

    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(SparkStreaming, self).create()

    def destory(self):
        super(SparkStreaming, self).destory()

    def doTest(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _test = self.getRunningServiceByName(self.app.appName, "SparkTest")
        _sparkStreamingContext = StreamingContext(_test.sc, 1)
        # Create the queue through which RDDs can be pushed to
        # a QueueInputDStream
        rddQueue = []
        for i in range(5):
            rddQueue += [_sparkStreamingContext.sparkContext.parallelize([j for j in range(1, 1001)], 10)]

        # Create the QueueInputDStream and use it do some processing
        inputStream = _sparkStreamingContext.queueStream(rddQueue)
        mappedStream = inputStream.map(lambda x: (x % 10, 1))
        reducedStream = mappedStream.reduceByKey(lambda a, b: a + b)
        reducedStream.pprint()

        _sparkStreamingContext.start()
        time.sleep(6)
        _sparkStreamingContext.stop(stopSparkContext=True, stopGraceFully=True)
