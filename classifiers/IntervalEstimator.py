from typing import *

from core.Instances import Instance


class IntervalEstimator():
    def predictIntervals(self,inst:Instance,confidenceLevel:float)->List[List]:pass
