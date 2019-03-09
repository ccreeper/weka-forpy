from typing import *
from core.neighboursearch.PerformanceStats import PerformanceStats
from Instances import Instances,Instance

class NearestNeighbourSearch():
    def __init__(self,insts:Instances=None):
        self.m_MeasurePerformance=False
        self.m_Stats=PerformanceStats()
        if insts is not None:
            self.m_Instances=insts

    def addInstanceInfo(self,ins:Instance):...
    def kNearestNeighbours(self,target:Instance,k:int)->Instances:...
    def getDistances(self):...