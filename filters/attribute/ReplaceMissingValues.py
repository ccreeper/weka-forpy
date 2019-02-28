from typing import *
from filters.Filter import Filter
from Instances import Instances,Instance

class ReplaceMissingValues(Filter):
    def __init__(self):
        super().__init__()

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.setOutputFormat(instanceInfo)
        self.m_ModesAndMeans=None
        return True