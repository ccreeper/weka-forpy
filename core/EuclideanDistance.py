import math
from typing import *

from core.NormalizableDistance import NormalizableDistance

from core.Instances import Instances, Instance
from core.neighboursearch.PerformanceStats import PerformanceStats


class EuclideanDistance(NormalizableDistance):
    def __init__(self,data:Instances=None):
        super().__init__(data)

    def distance(self, first:Instance, second:Instance,a0=None,a1=None):
        if a0 is None:
            return math.sqrt(super().distance(first,second,float('inf')))
        elif isinstance(a0,PerformanceStats):
            return math.sqrt(super().distance(first,second,float("inf"),a0))
        return super().distance(first,second,a0)

    def updateDistance(self,currDist:float,diff:float):
        result=currDist
        result+=diff*diff
        return result

    def postProcessDistances(self,distances:List):
        for i in range(len(distances)):
            distances[i]=math.sqrt(distances[i])