#!/usr/bin/env python3
import time
from base.supports.Base.BaseInService import BaseInService
from kafka import KafkaConsumer
from utils import pyUtils
import os


class Kafka(BaseInService):


    def __init__(self, belongToService_):
        super().__init__(belongToService_)

    def create(self):
        super(Kafka, self).create()

    def destory(self):
        super(Kafka, self).destory()

    def doTest(self):
        print(self.className + " - " + pyUtils.getCurrentRunningFunctionName() + "------------------")
        _topicName = "pro_bilog"
        local_url = ['网址:端口']
        real_url = ['ip:端口']
        _consumer = KafkaConsumer(
            _topicName,
            bootstrap_servers=local_url,
            group_id='test',
            request_timeout_ms=3000,
            session_timeout_ms=5000
        )
        # 获取test主题的分区信息
        print(_consumer.partitions_for_topic(_topicName))
        # 获取主题列表
        print(_consumer.topics())
        # 获取当前消费者订阅的主题
        print(_consumer.subscription())
        # 获取当前消费者topic、分区信息
        print(_consumer.assignment())
        # 获取当前消费者可消费的偏移量
        print(_consumer.beginning_offsets(_consumer.assignment()))
