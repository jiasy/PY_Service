#!/usr/bin/env python3


from base.supports.Service.BaseService import BaseService

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
