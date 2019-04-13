from typing import *
from classifiers.evaluation.Prediction import Prediction
from classifiers.evaluation.TwoClassStats import TwoClassStats
from Utils import Utils
from Instances import Instances,Instance
from Attributes import Attribute

class ThresholdCurve():
    RELATION_NAME = "ThresholdCurve"
    TRUE_POS_NAME = "True Positives"
    FALSE_NEG_NAME = "False Negatives"
    FALSE_POS_NAME = "False Positives"
    TRUE_NEG_NAME = "True Negatives"
    FP_RATE_NAME = "False Positive Rate"
    TP_RATE_NAME = "True Positive Rate"
    PRECISION_NAME = "Precision"
    RECALL_NAME = "Recall"
    FALLOUT_NAME = "Fallout"
    FMEASURE_NAME = "FMeasure"
    SAMPLE_SIZE_NAME = "Sample Size"
    LIFT_NAME = "Lift"
    THRESHOLD_NAME = "Threshold"

    def getCurve(self,predictions:List[Prediction],classIndex:int)->Instances:
        if len(predictions) == 0 or len(predictions[0].distribution()) <= classIndex:
            return None
        totPos=totNeg=0
        probs=self.getProbabilities(predictions,classIndex)

        for i in range(len(probs)):
            pred=predictions[i]
            if pred.actual() == Utils.missingValue():
                continue
            if pred.weight()<0:
                continue
            if pred.actual() == classIndex:
                totPos+=pred.weight()
            else:
                totNeg+=pred.weight()
        insts=self.makeHeader()
        sorted=Utils.sortDouble(probs)
        tc=TwoClassStats(totPos,totNeg,0,0)
        threshold=cumulativePos=cumulativeNeg=0
        for i in range(len(sorted)):
            if i == 0 or probs[sorted[i]] > threshold:
                tc.setTruePositive(tc.getTruePositive()-cumulativePos)
                tc.setFalseNegative(tc.getFalseNegative()+cumulativePos)
                tc.setFalsePositive(tc.getFalsePositive()-cumulativeNeg)
                tc.setTrueNegative(tc.getTrueNegative()+cumulativeNeg)
                threshold=probs[sorted[i]]
                insts.add(self.makeInstance(tc,threshold))
                cumulativePos=0
                cumulativeNeg=0
                if i == len(sorted)-1:
                    break
            pred=predictions[sorted[i]]
            if pred.actual() == Utils.missingValue():
                continue
            if pred.weight() < 0:
                continue
            if pred.actual() == classIndex:
                cumulativePos+=pred.weight()
            else:
                cumulativeNeg+=pred.weight()
        if tc.getFalseNegative() != totPos or tc.getTrueNegative() != totNeg:
            tc=TwoClassStats(0,0,totNeg,totPos)
            threshold=probs[sorted[-1]]+10e-6
            insts.add(self.makeInstance(tc,threshold))
        return insts

    def makeInstance(self,tc:TwoClassStats,prob:float)->Instance:
        count=0
        vals=[0]*13
        vals[count]=tc.getTruePositive()
        count+=1
        vals[count]=tc.getFalseNegative()
        count+=1
        vals[count]=tc.getFalsePositive()
        count+=1
        vals[count]=tc.getTrueNegative()
        count+=1
        vals[count]=tc.getFalsePositiveRate()
        count+=1
        vals[count]=tc.getTruePositiveRate()
        count+=1
        vals[count]=tc.getPrecision()
        count+=1
        vals[count]=tc.getRecall()
        count+=1
        vals[count]=tc.getFallout()
        count+=1
        vals[count]=tc.getFMeasure()
        count+=1
        ss=(tc.getTruePositive()+tc.getFalsePositive())/(tc.getTruePositive()+tc.getFalsePositive()+tc.getTrueNegative()+tc.getFalseNegative())
        vals[count]=ss
        count+=1
        expectedByChance=ss*(tc.getTruePositive()+tc.getFalseNegative())
        if expectedByChance < 1:
            vals[count]=Utils.missingValue()
        else:
            vals[count]=tc.getTruePositive()/expectedByChance
        count+=1
        vals[count]=prob
        return Instance(1.0,vals)

    def makeHeader(self)->Instances:
        fv=[]
        fv.append(Attribute(self.TRUE_POS_NAME))
        fv.append(Attribute(self.FALSE_NEG_NAME))
        fv.append(Attribute(self.FALSE_POS_NAME))
        fv.append(Attribute(self.TRUE_NEG_NAME))
        fv.append(Attribute(self.FP_RATE_NAME))
        fv.append(Attribute(self.TP_RATE_NAME))
        fv.append(Attribute(self.PRECISION_NAME))
        fv.append(Attribute(self.RECALL_NAME))
        fv.append(Attribute(self.FALLOUT_NAME))
        fv.append(Attribute(self.FMEASURE_NAME))
        fv.append(Attribute(self.SAMPLE_SIZE_NAME))
        fv.append(Attribute(self.LIFT_NAME))
        fv.append(Attribute(self.THRESHOLD_NAME))
        return Instances(self.RELATION_NAME,fv,100)

    def getProbabilities(self,predictions:List[Prediction],classIndex:int):
        probs=[0]*len(predictions)
        for i in range(len(probs)):
            pred=predictions[i]
            probs[i]=pred.distribution()[classIndex]
        return probs

    @classmethod
    def getROCArea(cls,tcurve:Instances):
        n=tcurve.numInstances()
        if cls.RELATION_NAME != tcurve.relationName() or n == 0:
            return float('nan')
        tpInd=tcurve.attribute(cls.TRUE_POS_NAME).index()
        fpInd=tcurve.attribute(cls.FALSE_POS_NAME).index()
        tpVals=tcurve.attributeToDoubleArray(tpInd)
        fpVals=tcurve.attributeToDoubleArray(fpInd)
        area=cumNeg=0
        totalPos=tpVals[0]
        totalNeg=fpVals[0]
        for i in range(n):
            if i<n-1:
                cip=tpVals[i]-tpVals[i+1]
                cin=fpVals[i]-fpVals[i+1]
            else:
                cip=tpVals[n-1]
                cin=fpVals[n-1]
            area+=cip*(cumNeg+(0.5*cin))
            cumNeg+=cin
        if totalNeg*totalPos == 0:
            if area == 0:
                return float("nan")
            elif area > 0:
                return float("inf")
            else:
                return float("-inf")
        area/=(totalNeg*totalPos)
        return area

    @classmethod
    def getPRCArea(cls,tcurve:Instances):
        n = tcurve.numInstances()
        if cls.RELATION_NAME != tcurve.relationName() or n == 0:
            return float('nan')
        pInd = tcurve.attribute(cls.PRECISION_NAME).index()
        rInd = tcurve.attribute(cls.RECALL_NAME).index()
        pVals = tcurve.attributeToDoubleArray(pInd)
        rVals = tcurve.attributeToDoubleArray(rInd)
        area = 0
        xlast = rVals[n-1]
        for i in range(n-2,-1,-1):
            recallDelta=rVals[i]-xlast
            area+=pVals[i]*recallDelta
            xlast=rVals[i]
        if area == 0:
            return Utils.missingValue()
        return area