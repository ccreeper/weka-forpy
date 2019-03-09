from typing import *
from Instances import Instances,Instance
from NormalizableDistance import NormalizableDistance
from core.neighboursearch.PerformanceStats import PerformanceStats
import math

class EuclideanDistance(NormalizableDistance):
    def __init__(self,data:Instances=None):
        super().__init__(data)

    def distance(self, first:Instance, second:Instance,a0=None,a1=None):
        if a0 is None or isinstance(a0,PerformanceStats):
            return math.sqrt(self.distance(first,second,float("inf"),a0))
        return super().distance(first,second,a0,a1)

    def updateDistance(self,currDist:float,diff:float):
        result=currDist
        result+=diff*diff
        return result

    def postProcessDistances(self,distances:List):
        for i in range(len(distances)):
            distances[i]=math.sqrt(distances[i])