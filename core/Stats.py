import math
from functools import partial

class Stats():
    equal=partial(math.isclose,rel_tol=1e-6)
    def __init__(self):
        self.reset()

    def add(self,value:float,weight:float=1):
        if weight<0:
            self.subtract(value,-weight)
            return
        if self.isInvalid():
            return
        if math.isinf(weight) or math.isnan(weight) or math.isinf(value) or math.isnan(value):
            self.goInvalid()
            return
        if weight == 0:
            return

        newCount=self.count+weight
        if self.count<0 and (newCount>0 or self.equal(newCount,0)):
            self.reset()
            return
        self.count=newCount
        if self.count<0:
            return

        weightedValue = value * weight
        self.sum += weightedValue
        self.sumSq += value * weightedValue
        if math.isnan(self.mean):
            self.mean=value
            self.stdDevFactor=0
        else:
            delta=weight*(value-self.mean)
            self.mean += delta/self.count
            self.stdDevFactor += delta*(value-self.mean)

        if math.isnan(self.min):
            self.min=self.max=value
        elif value<self.min:
            self.min=value
        elif value>self.max:
            self.max=value

    def subtract(self,value:float,weight:float=1):
        if weight<0:
            self.add(value,-weight)
            return
        if self.isInvalid():
            return
        if math.isinf(weight) or math.isnan(weight) or math.isinf(value) or math.isnan(value):
            self.goInvalid()
            return
        if weight == 0:
            return
        self.count -= weight

        if self.equal(self.count,0):
            self.reset()
            return
        elif self.count<0:
            self.negativeCount()
            return

        weightedValue=value*weight
        self.sum -= weightedValue
        self.sumSq -= value*weightedValue
        delta=weight*(value-self.mean)
        self.mean -= delta/self.count
        self.stdDevFactor -= delta*(value-self.mean)

    def calculateDerived(self):
        if self.count <= 1 :
            self.stdDev = float("nan")
            return
        self.stdDev = self.stdDevFactor/(self.count - 1)
        if self.stdDev < 0:
            self.stdDev = 0
            return
        self.stdDev = math.sqrt(self.stdDev)

    def toString(self):
        return"Count   " + str("%.8f" % self.count) + '\n'\
                + "Min     " + str("%.8f" % self.min) + '\n'\
                + "Max     " + str("%.8f" % self.max) + '\n'\
                + "Sum     " + str("%.8f" % self.sum) + '\n'\
                + "SumSq   " + str("%.8f" % self.sumSq) + '\n'\
                + "Mean    " + str("%.8f" % self.mean) + '\n'\
                + "StdDev  " + str("%.8f" % self.stdDev) + '\n'

    def reset(self):
        self.count=0
        self.sum=0
        self.sumSq=0
        self.stdDev=float("nan")
        self.mean=float("nan")
        self.min=float("nan")
        self.max=float("nan")
        self.stdDevFactor=0

    def negativeCount(self):
        self.sum=float("nan")
        self.sumSq=float("nan")
        self.stdDev=float("nan")
        self.mean=float("nan")
        self.min=float("nan")
        self.max=float("nan")

    def goInvalid(self):
        self.count=float("nan")
        self.negativeCount()

    def isInvalid(self)->bool:
        return math.isnan(self.count)


