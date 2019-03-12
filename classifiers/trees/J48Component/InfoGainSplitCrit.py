from typing import *
from classifiers.trees.J48Component.EntropyBasedSplitCrit import EntropyBasedSplitCrit
from classifiers.trees.J48Component.Distribution import Distribution
from Utils import Utils

class InfoGainSplitCrit(EntropyBasedSplitCrit):
    def splitCritValue(self,bags:Distribution,totalNoInst:float=None,oldEnt:float=None):
        if totalNoInst is None:
            numerator=self.oldEnt(bags)-self.newEnt(bags)
            if Utils.equal(numerator,0):
                return float("inf")
            return bags.total()/numerator
        else:
            noUnknown=totalNoInst-bags.total()
            unknowRate=noUnknown/totalNoInst
            if oldEnt is not None:
                numerator = oldEnt - self.newEnt(bags)
            else:
                numerator=self.oldEnt(bags)-self.newEnt(bags)
            numerator=(1-unknowRate)*numerator
            if Utils.equal(numerator,0):
                return 0
            return numerator/bags.total()