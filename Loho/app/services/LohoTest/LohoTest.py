#!/usr/bin/env python3
import os

from base.supports.Service.BaseService import BaseService

from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, Row

from utils import dictUtils
from utils import fileUtils
from utils import resUtils
import json
from utils import pyUtils
from sqlalchemy.engine import create_engine
import pandas as pd
import pandas.io.sql as sql


class LohoTest(BaseService):

    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(LohoTest, self).create()
        # # 输出 回放的格式
        # _recoderJsonDict = fileUtils.dictFromJsonFile(
        #     "/Volumes/Files/develop/loho/mini-game/miniclient/assets/resources/configs/replay/replay.json")
        # dictUtils.showDictStructure(_recoderJsonDict)

    def destory(self):
        super(LohoTest, self).destory()
