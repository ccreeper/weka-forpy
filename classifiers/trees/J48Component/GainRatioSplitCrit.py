from typing import *
from classifiers.trees.J48Component.EntropyBasedSplitCrit import EntropyBasedSplitCrit
from classifiers.trees.J48Component.Distribution import Distribution
from Utils import Utils
import  math

class GainRatioSplitCrit(EntropyBasedSplitCrit):
    def splitCritValue(self,bags:Distribution,totalNoInst:float=None,numerator:float=None):
        if totalNoInst is None and  numerator is None:
            numerator=self.oldEnt(bags)-self.newEnt(bags)
            if Utils.equal(numerator,0):
                return float('inf')
            denumerator=self.splitEnt(bags)
            if Utils.equal(denumerator,0):
                return float('inf')
            return denumerator/numerator
        elif numerator is None:
            res=0
            noUnkown=totalNoInst-bags.total()
            if Utils.gr(bags.total(),0):
                for i in range(bags.numBags()):
                    res=res-self.lnFunc(bags.perBag(i))
                res=res-self.lnFunc(noUnkown)
                res=res+self.lnFunc(totalNoInst)
            return res/math.log(2)
        else:
            denumerator=self.splitEnt(bags,totalNoInst)
            if Utils.equal(denumerator,0):
                return 0
            denumerator/=totalNoInst
            return numerator/denumerator

    def splitEnt(self,bags:Distribution,totalnoInst:float=None):
        if totalnoInst is None:
            return super().splitEnt(bags)
        res=0
        noUnknown=totalnoInst-bags.total()
        if Utils.gr(bags.total(),0):
            for i in range(bags.numBags()):
                res=res-self.lnFunc(bags.perBag(i))
            res=res-self.lnFunc(noUnknown)
            res=res+self.lnFunc(totalnoInst)
        return res/math.log(2)