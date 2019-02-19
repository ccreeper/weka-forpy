import math
from typing import *

import numpy as np
from classifiers.evaluation import Prediction

from Instances import Instances, Instance
from Utils import Utils
from classifiers.evaluation.NominalPrediction import NominalPrediction
from classifiers.evaluation.NumericPrediction import NumericPrediction
from classifiers.Classifier import Classifier
from classifiers.ConditionalDensityEstimator import ConditionalDensityEstimator
from classifiers.IntervalEstimator import IntervalEstimator
from estimators.UnivariateKernelEstimator import UnivariateKernelEstimator


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
        self.m_WithClass=0
        self.m_Unclassified=0
        self.m_SumKBInfo=0
        self.m_SumSchemeEntropy=0
        self.m_SumPriorEntropy=0
        self.m_SumErr=self.m_SumAbsErr=self.m_SumSqrErr=self.m_SumPriorAbsErr=self.m_SumPriorSqrErr=0
        self.m_ConfLevel=0.95
        self.m_TotalCoverage=self.m_TotalSizeOfRegions=0
        self.m_MissingClass=0
        self.m_Incorrect=self.m_Correct=0
        self.m_DiscardPredictions=False
        self.m_CoverageStatisticsAvailable=True
        self.m_ComplexityStatisticsAvailable=True
        self.m_SumClass=self.m_SumSqrClass=self.m_SumPredicted=self.m_SumSqrPredicted=self.m_SumClassPredicted=0

        self.m_Predictions=None     #type:List[Prediction]
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

    def evaluationForSingleInstance(self, a0, instance:Instance, storePredictions:bool):
        if isinstance(a0,List):
            if self.m_ClassIsNominal:
                pred=Utils.maxIndex(a0)
                if a0[int(pred)] <= 0:
                    pred=Utils.missingValue()
                self.updateStatsForClassifier(a0, instance)
                if storePredictions and not self.m_DiscardPredictions:
                    if self.m_Predictions is None:
                        self.m_Predictions=[]
                    self.m_Predictions.append(NominalPrediction(instance.classValue(), a0, instance.weight()))
            else:
                pred=a0[0]
                self.updateStatsForPredictor(pred,instance)
                if storePredictions and not self.m_DiscardPredictions:
                    if self.m_Predictions is None:
                        self.m_Predictions=[]
                    self.m_Predictions.append(NumericPrediction(instance.classValue(),pred,instance.weight()))
            return pred
        elif isinstance(a0,Classifier):
            classMissing=instance.copy()
            classMissing.setDataset(instance.dataset())
            #TODO
            # if isinstance(a0,InputMappedClassifier)
            # else:
            classMissing.setClassMissing()

            pred=self.evaluationForSingleInstance(a0.distributionForInstance(classMissing),instance,storePredictions)
            if not self.m_ClassIsNominal:
                if not instance.classIsMissing() and not Utils.isMissingValue(pred):
                    if isinstance(a0,IntervalEstimator):
                        self.updateStatsForIntervalEstimator(a0,classMissing,instance.classValue())
                    else:
                        self.m_CoverageStatisticsAvailable=False
                    if isinstance(a0,ConditionalDensityEstimator):
                        self.updateStatsForConditionalDensityEstimator(a0,classMissing,instance.classValue())
                    else:
                        self.m_ComplexityStatisticsAvailable=False
            return pred



    def updateStatsForConditionalDensityEstimator(self,classifier:ConditionalDensityEstimator,classMissing:Instance,classValue:float):
        if self.m_PriorEstimator is None:
            self.setNumericPriorsFromBuffer()
        self.m_SumSchemeEntropy-=classifier.logDensity(classMissing,classValue)*classMissing.weight()/math.log(2)
        self.m_SumPriorEntropy-=self.m_PriorEstimator.logDensity(classValue)*classMissing.weight()/math.log(2)


    def setNumericPriorsFromBuffer(self):
        self.m_PriorEstimator=UnivariateKernelEstimator()
        for i in range(self.m_NumTrainClassVals):
            self.m_PriorEstimator.addValue(self.m_TrainClassVals[i],self.m_TrainClassWeights[i])

    def updateStatsForIntervalEstimator(self,classifier:IntervalEstimator,classMissing:Instance,classValue:float):
        preds=classifier.predictIntervals(classMissing,self.m_ConfLevel)
        if self.m_Predictions is not None:
            self.m_Predictions[-1].setPredictionIntervals(preds)
        for pred in preds:
            self.m_TotalSizeOfRegions+=classMissing.weight()*(pred[1]-pred[0])/(self.m_MaxTarget-self.m_MinTarget)
        for pred in preds:
            if pred[1]>=classValue and pred[0]<=classValue:
                self.m_TotalCoverage+=classMissing.weight()
                break


    def updateStatsForPredictor(self,predictedValue:float,instance:Instance):
        if not instance.classIsMissing():
            self.m_WithClass+=instance.weight()
            if Utils.isMissingValue(predictedValue):
                self.m_Unclassified+=instance.weight()
                return
            self.m_SumClass+=instance.weight()*instance.classValue()
            self.m_SumSqrClass+=instance.weight()*instance.classValue()*instance.classAttribute()
            self.m_SumClassPredicted+=instance.weight()*instance.classValue()*predictedValue
            self.m_SumPredicted+=instance.weight()*predictedValue
            self.m_SumSqrPredicted+=instance.weight()*predictedValue*predictedValue
            self.updateNumericScores(self.makeDistribution(predictedValue),self.makeDistribution(instance.classValue()),instance.weight())
        else:
            self.m_MissingClass+=instance.weight()

    def evaluateModelOnceAndRecordPrediction(self,classifier:Classifier,instance:Instance):
        return self.evaluationForSingleInstance(classifier,instance,True)

    def updateStatsForClassifier(self,predictedDistribution:List,instance:Instance):
        actualClass=instance.classValue()
        if not instance.classIsMissing():
            self.updateMargins(predictedDistribution,actualClass,instance.weight())
            predictedClass=-1
            bestProb=0
            for i in range(self.m_NumClasses):
                if predictedDistribution[i] > bestProb:
                    predictedClass=i
                    bestProb=predictedDistribution[i]
            self.m_WithClass+=instance.weight()
            if predictedClass < 0:
                self.m_Unclassified+=instance.weight()
                return
            predictedProb=max(float('-inf'),predictedDistribution[actualClass])
            priorProb=max(float('-inf'),self.m_ClassPriors[actualClass]/self.m_ClassPriorsSum)
            if predictedProb >= priorProb:
                self.m_SumKBInfo+=(Utils.log2(predictedProb)-Utils.log2(priorProb))*instance.weight()
            else:
                self.m_SumKBInfo-=(Utils.log2(1-predictedProb)-Utils.log2(1-priorProb))*instance.weight()
            self.m_SumSchemeEntropy-=Utils.log2(predictedProb)*instance.weight()
            self.m_SumPriorEntropy-=Utils.log2(priorProb)*instance.weight()
            self.updateNumericScores(predictedDistribution,self.makeDistribution(instance.classValue()),instance.weight())
            indices=Utils.stableSort(predictedDistribution)
            sum=sizeOfregions=0
            for i in range(len(predictedDistribution)-1,-1,-1):
                if sum >= self.m_ConfLevel:
                    break
                sum+=predictedDistribution[indices[i]]
                sizeOfregions+=1
                if actualClass == indices[i]:
                    self.m_TotalCoverage+=instance.weight()
            self.m_TotalSizeOfRegions+=instance.weight()*sizeOfregions/(self.m_MaxTarget-self.m_MinTarget)
            self.m_ConfusionMatrix[actualClass][predictedClass]+=instance.weight()
            if predictedClass != actualClass:
                self.m_Incorrect+=instance.weight()
            else:
                self.m_Correct+=instance.weight()
        else:
            self.m_MissingClass+=instance.weight()





    def makeDistribution(self,predictedClass:float):
        result=[0]*self.m_NumClasses
        if Utils.isMissingValue(predictedClass):
            return result
        if self.m_ClassIsNominal:
            result[int(predictedClass)]=1
        else:
            result[0]=predictedClass
        return result

    def updateNumericScores(self,predicted:List,actual:List,weight:float):
        sumErr=sumAbsErr=sumSqrErr=sumPriorAbsErr=sumPriorSqrErr=0
        for i in range(self.m_NumClasses):
            diff=predicted[i]-actual[i]
            sumErr+=diff
            sumAbsErr+=math.fabs(diff)
            sumSqrErr+=diff*diff
            diff=(self.m_ClassPriors[i]/self.m_ClassPriorsSum)-actual[i]
            sumPriorAbsErr+=math.fabs(diff)
            sumPriorSqrErr+=diff*diff
        self.m_SumErr+=weight*sumErr/self.m_NumClasses
        self.m_SumAbsErr+=weight*sumAbsErr/self.m_NumClasses
        self.m_SumSqrErr+=weight*sumSqrErr/self.m_NumClasses
        self.m_SumPriorAbsErr+=weight*sumPriorAbsErr/self.m_NumClasses
        self.m_SumPriorSqrErr+=weight*sumPriorSqrErr/self.m_NumClasses


    def updateMargins(self,predictedDistribution:List,actualClass:int,weight:float):
        probActual=predictedDistribution[actualClass]
        probNext=0
        for i in range(self.m_NumClasses):
            if i != actualClass and predictedDistribution[i] > probNext:
                probNext=predictedDistribution[i]
        margin=probActual-probNext
        bin=int((margin+1)/2*self.k_MarginResolution)
        self.m_MarginCounts[bin]+=weight


    @classmethod
    def getAllEvaluationMetricNames(cls):
        allEvals=[]     #type:List[str]
        for s in cls.BUILT_IN_EVAL_METRICS:
            allEvals.append(s)
        return allEvals





