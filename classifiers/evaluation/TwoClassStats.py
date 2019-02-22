from typing import *

class TwoClassStats():
    CATEGORY_NAMES =["negative", "positive"]
    def __init__(self,tp:float,fp:float,tn:float,fn:float):
        self.setTruePositive(tp)
        self.setFalsePositive(fp)
        self.setTrueNegative(tn)
        self.setFalseNegative(fn)

    def __str__(self):
        res=""
        res+=str(self.getTruePositive())+' '
        res+=str(self.getFalseNegative())+' '
        res+=str(self.getTrueNegative())+' '
        res+=str(self.getFalsePositive())+' '
        res+=str(self.getFalsePositiveRate())+' '
        res+=str(self.getTruePositiveRate())+' '
        res+=str(self.getPrecision())+' '
        res+=str(self.getRecall())+' '
        res+=str(self.getFMeasure())+' '
        res+=str(self.getFallout())+' '
        return res

    def setTruePositive(self,tp:float):
        self.m_TruePos=tp

    def setFalsePositive(self,fp):
        self.m_FalsePos=fp

    def setTrueNegative(self,tn):
        self.m_TrueNeg=tn

    def setFalseNegative(self,fn):
        self.m_FalseNeg=fn

    def getTruePositive(self):
        return self.m_TruePos

    def getFalsePositive(self):
        return self.m_FalsePos

    def getTrueNegative(self):
        return self.m_TrueNeg

    def getFalseNegative(self):
        return self.m_FalseNeg

    def getTruePositiveRate(self):
        if self.m_TruePos+self.m_FalseNeg == 0:
            return float('nan')
        return self.m_TruePos/(self.m_TruePos+self.m_FalseNeg)

    def getFalsePositiveRate(self):
        if self.m_FalsePos+self.m_TrueNeg == 0:
            return float("nan")
        return self.m_FalsePos/(self.m_FalsePos+self.m_TrueNeg)

    def getPrecision(self):
        if self.m_TruePos+self.m_FalsePos == 0:
            return float('nan')
        return self.m_TruePos/(self.m_TruePos+self.m_FalsePos)

    def getRecall(self):
        return self.getTruePositiveRate()

    def getFMeasure(self):
        precision=self.getPrecision()
        recall=self.getRecall()
        if precision+recall == 0:
            return float('nan')
        return 2*precision*recall/(precision+recall)

    def getFallout(self):
        if self.m_TruePos+self.m_FalsePos == 0:
            return float('nan')
        return self.m_FalsePos/(self.m_TruePos+self.m_FalsePos)

