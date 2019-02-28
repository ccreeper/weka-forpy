from typing import *
from Instances import Instances,Instance
from NormalizableDistance import NormalizableDistance
import math

class EuclideanDistance(NormalizableDistance):
    def __init__(self,data:Instances=None):
        super().__init__(data)

    def distance(self,first:Instance,second:Instance,cutOffValue:float=None):
        if cutOffValue is None:
            return math.sqrt(super().distance(first,second,float('inf')))
        return super().distance(first,second,cutOffValue)

    def updateDistance(self,currDist:float,diff:float):
        result=currDist
        result+=diff*diff
        return result