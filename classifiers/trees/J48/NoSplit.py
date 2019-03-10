from typing import *
from Instances import Instances,Instance
from classifiers.trees.J48.Distribution import Distribution
from classifiers.trees.J48.ClassifierSplitModel import ClassifierSplitModel

class NoSplit(ClassifierSplitModel):
    def __init__(self,distribution:Distribution):
        super().__init__()
        self.m_distribution=Distribution(distribution)
        self.m_numSubsets=1

    def buildClassifer(self,instances:Instances):
        self.m_distribution=Distribution(instances)
        self.m_numSubsets=1

    def weights(self,instance:Instance):
        return None

    def whichSubset(self,instance:Instance):
        return 0

    def leftSide(self,data:Instances):
        return ""

    def rightSide(self,index:int,data:Instances):
        return ""
