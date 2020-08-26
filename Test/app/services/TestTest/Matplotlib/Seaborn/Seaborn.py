'''
http://seaborn.pydata.org/

'''

from base.supports.Base.Base import Base
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Seaborn(Base):
    def __init__(self, sm_):
        super().__init__(sm_)

    def create(self):
        super(Seaborn, self).create()
        sns.set(style="darkgrid")

    def destory(self):
        super(Seaborn, self).destory()
