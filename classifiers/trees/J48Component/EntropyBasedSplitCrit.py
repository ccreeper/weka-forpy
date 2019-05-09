import math

from classifiers.trees.J48Component.Distribution import Distribution
from core.Utils import Utils


class EntropyBasedSplitCrit():
    def oldEnt(self,bags:Distribution):
        res=0
        for j in range(bags.numClasses()):
            res=res+self.lnFunc(bags.perClass(j))
        return (self.lnFunc(bags.total())-res)/math.log(2)

    def newEnt(self,bags:Distribution):
        res=0
        for i in range(bags.numBags()):
            for j in range(bags.numClasses()):
                res=res+self.lnFunc(bags.perClassPerBag(i,j))
            res=res-self.lnFunc(bags.perBag(i))
        return -(res/math.log(2))


    def lnFunc(self,num:float):
        if num<1e-6:
            return 0
        return Utils.lnFunc(num)

    def splitEnt(self,bags:Distribution):
        res=0
        for i in range(bags.numBags()):
            res=res+self.lnFunc(bags.perBag(i))
        return (self.lnFunc(bags.total())-res)/math.log(2)