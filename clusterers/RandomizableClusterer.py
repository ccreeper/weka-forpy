from typing import *
from clusterers.AbstractClusterer import AbstractClusterer
from OptionHandler import OptionHandler

class RandomizableClusterer(AbstractClusterer,OptionHandler):
    propertyList = AbstractClusterer.propertyList[:]
    methodList = AbstractClusterer.methodList[:]
    propertyList.append('seed')
    def __init__(self):
        super().__init__()
        self.Seed=1
        self.seed=self.Seed

    def setSeed(self,value:int):
        self.seed=value

    def getSeed(self):
        return self.seed
