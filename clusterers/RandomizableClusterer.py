from typing import *
from clusterers.AbstractClusterer import AbstractClusterer
from OptionHandler import OptionHandler

class RandomizableClusterer(AbstractClusterer,OptionHandler):
    propertyList = AbstractClusterer.propertyList[:]
    methodList = AbstractClusterer.methodList[:]
    propertyList.append('seed')
    def __init__(self):
        super().__init__()
        self.m_SeedDefault=1
        self.seed=self.m_SeedDefault

    def setSeed(self,value:int):
        self.seed=value

    def getSeed(self):
        return self.seed
