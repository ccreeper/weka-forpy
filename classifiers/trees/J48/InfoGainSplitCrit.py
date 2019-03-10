from typing import *
from classifiers.trees.J48.EntropyBasedSplitCrit import EntropyBasedSplitCrit
from classifiers.trees.J48.Distribution import Distribution
from Utils import Utils

class InfoGainSplitCrit(EntropyBasedSplitCrit):
    def splitCritValue(self,bags:Distribution,totalNoInst:float):
        noUnknown=totalNoInst-bags.total()
        unknowRate=noUnknown/totalNoInst
        numerator=self.oldEnt(bags)-self.newEnt(bags)
        numerator=(1-unknowRate)*numerator
        if Utils.equal(numerator,0):
            return 0
        return numerator/bags.total()