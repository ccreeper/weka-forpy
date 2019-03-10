from typing import *
from classifiers.trees.J48.EntropyBasedSplitCrit import EntropyBasedSplitCrit
from classifiers.trees.J48.Distribution import Distribution
from Utils import Utils
import  math

class GainRatioSplitCrit(EntropyBasedSplitCrit):
    def splitCritValue(self,bags:Distribution,totalNoInst:float,numerator:float):
        denumerator=self.splitEnt(bags,totalNoInst)
        if Utils.equal(denumerator,0):
            return 0
        denumerator/=totalNoInst
        return numerator/denumerator

    def splitEnt(self,bags:Distribution,totalnoInst:float):
        res=0
        noUnknown=totalnoInst-bags.total()
        if Utils.gr(bags.total(),0):
            for i in range(bags.numBags()):
                res=res-self.lnFunc(bags.perBag(i))
            res=res-self.lnFunc(noUnknown)
            res=res+self.lnFunc(totalnoInst)
        return res/math.log(2)