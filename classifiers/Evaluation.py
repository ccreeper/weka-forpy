from typing import *
from Instances import Instances
import numpy as np

class Evaluation():
    k_MarginResolution=500
    BUILT_IN_EVAL_METRICS=["Correct",
          "Incorrect", "Kappa", "Total cost", "Average cost", "KB relative",
          "KB information", "Correlation", "Complexity 0", "Complexity scheme",
          "Complexity improvement", "MAE", "RMSE", "RAE", "RRSE", "Coverage",
          "Region size", "TP rate", "FP rate", "Precision", "Recall", "F-measure",
          "MCC", "ROC area", "PRC area"]
    def __init__(self,data:Instances):
        self.m_Header=Instances(data,0)
        self.m_NumClasses=data.numClasses()
        self.m_NumFolds=1
        self.m_metricsToDisplay=[]
        self.m_ClassIsNominal=data.classAttribute().isNominal()
        if self.m_ClassIsNominal:
            self.m_ConfusionMatrix=[[0]*self.m_NumClasses for i in range(self.m_NumClasses)]       #type:List[List[float]]
            self.m_ClassNames=[]        #type:List[str]
            for i in range(self.m_NumClasses):
                self.m_ClassNames.append(data.classAttribute().value(i))
        self.m_ClassPriors=[0]*self.m_NumClasses       #type:List[float]
        self.setPriors(data)
        self.m_MarginCounts=[0]*(self.k_MarginResolution+1)
        for s in self.BUILT_IN_EVAL_METRICS:
            if s.lower() != "coverage" and s.lower() != "region size":
                self.m_metricsToDisplay.append(s.lower())



    def setPriors(self,train:Instances):
        self.m_NoPriors=False
        if not self.m_ClassIsNominal:
            self.m_NumTrainClassVals=0
            self.m_TrainClassVals=None
            self.m_TrainClassWeights=None
            self.m_PriorEstimator=None
            self.m_MinTarget=float("inf")
            self.m_MaxTarget=float("inf")
            for i in range(train.numInstances()):
                currentInst=train.instance(i)
                if not currentInst.classIsMissing():
                    self.addNumericTrainClass(currentInst.classValue(),currentInst.weight())
            self.m_ClassPriors[0]=self.m_ClassPriorsSum=0
            for i in range(train.numInstances()):
                if not train.instance(i).classIsMissing():
                    self.m_ClassPriors[0]+=train.instance(i).classValue()*train.instance(i).weight()
                    self.m_ClassPriorsSum+=train.instance(i).weight()
        else:
            for i in range(self.m_NumClasses):
                self.m_ClassPriors[i]=1
            self.m_ClassPriorsSum=self.m_NumClasses
            for i in range(train.numInstances()):
                if not train.instance(i).classIsMissing():
                    self.m_ClassPriors[int(train.instance(i).classValue())]+=train.instance(i).weight()
                    self.m_ClassPriorsSum+=train.instance(i).weight()
            self.m_MaxTarget=self.m_NumClasses
            self.m_MinTarget=0


    def addNumericTrainClass(self,classValue:float,weight:float):
        if classValue > self.m_MaxTarget:
            self.m_MaxTarget=classValue
        if classValue < self.m_MinTarget:
            self.m_MinTarget=classValue
        if self.m_TrainClassVals is None:
            self.m_TrainClassVals=[0]*100        #type:List[float]
            self.m_TrainClassWeights=[0]*100         #type:List[float]
        if self.m_NumTrainClassVals == len(self.m_TrainClassVals):
            self.m_TrainClassVals=np.hstack((self.m_TrainClassVals,[0]*len(self.m_TrainClassVals)))
            self.m_TrainClassWeights=np.hstack((self.m_TrainClassWeights,[0]*len(self.m_TrainClassWeights)))
        self.m_TrainClassVals[self.m_NumTrainClassVals]=classValue
        self.m_TrainClassWeights[self.m_NumTrainClassVals]=weight
        self.m_NumTrainClassVals+=1

    def setMetricsToDisplay(self,display:List[str]):
        self.m_metricsToDisplay.clear()
        for s in display:
            self.m_metricsToDisplay.append(s.strip().lower())

    @classmethod
    def getAllEvaluationMetricNames(cls):
        allEvals=[]     #type:List[str]
        for s in cls.BUILT_IN_EVAL_METRICS:
            allEvals.append(s)
        return allEvals





