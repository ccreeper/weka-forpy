from typing import *
import math

class UnivariateKernelEstimator():
    CONST=-0.5*math.log(2*math.pi)
    def __init__(self):
        self.m_TM=dict()        #type:Dict[float,float]
        self.m_WeightedSum=0
        self.m_WeightedSumSquared=0
        self.m_SumOfWeights=0
        self.m_Width=float("inf")
        self.m_Exponent=-0.25
        self.m_MinWidth=1e-6
        self.m_Threshold=1e-6
        self.m_NumIntervals=1000

    def addValue(self,value:float,weight:float):
        self.m_WeightedSum+=value*weight
        self.m_WeightedSumSquared+=value*value*weight
        self.m_SumOfWeights+=weight
        if self.m_TM.get(value) is None:
            self.m_TM.update({value:weight})
        else:
            self.m_TM.update({value:self.m_TM.get(value)+weight})

    def logDensity(self,value:float):
        self.updateWidth()
        sums=[float('nan')]*2
        self.runningSum(dict({k:v for k,v in self.m_TM.items() if k>=value}),value,sums)
        keys=list([i for i in self.m_TM.keys() if i<value])
        keys.reverse()
        self.runningSum(dict({k:self.m_TM.get(k) for k in keys}),value,sums)
        return sums[0]-math.log(self.m_SumOfWeights)


    def runningSum(self,c:Dict[float,float],value:float,sums:List):
        offset=self.CONST-math.log(self.m_Width)
        logFactor=math.log(self.m_Threshold)-math.log(1-self.m_Threshold)
        logSumOfWeights=math.log(self.m_SumOfWeights)

        for key,value in c.items():
            if value>0:
                diff=(key-value)/self.m_Width
                logDensity=offset-0.5*diff*diff
                logWeight=math.log(value)
                sums[0]=self.logOfSum(sums[0],logWeight+logDensity)
                sums[1]=self.logOfSum(sums[1],logWeight)
                if logDensity+logSumOfWeights < self.logOfSum(logFactor+sums[0],logDensity+sums[1]):
                    break

    def logOfSum(self,logOfX:float,logOfY:float):
        if math.isnan(logOfX):
            return logOfY
        if math.isnan(logOfY):
            return logOfX
        if logOfX > logOfY:
            return logOfX+math.log(1+math.exp(logOfY-logOfX))
        else:
            return logOfY+math.log(1+math.exp(logOfX-logOfY))

    def updateWidth(self):
        if self.m_SumOfWeights >0:
            mean=self.m_WeightedSum/self.m_SumOfWeights
            variance=self.m_WeightedSumSquared/self.m_SumOfWeights-mean*mean
            if variance<0:
                variance=0
            self.m_Width=math.sqrt(variance)*math.pow(self.m_SumOfWeights,self.m_Exponent)
            if self.m_Width<=self.m_MinWidth:
                self.m_Width=self.m_MinWidth
        else:
            self.m_Width=float("inf")