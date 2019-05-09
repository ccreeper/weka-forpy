import copy
import math
from typing import *

import numpy as np
from core.Instances import Instances, Instance

from classifiers.Classifier import Classifier
from classifiers.ConditionalDensityEstimator import ConditionalDensityEstimator
from classifiers.IntervalEstimator import IntervalEstimator
from classifiers.evaluation import Prediction
from classifiers.evaluation.NominalPrediction import NominalPrediction
from classifiers.evaluation.NumericPrediction import NumericPrediction
from classifiers.evaluation.ThresholdCurve import ThresholdCurve
from core.Utils import Utils
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

    def predictions(self):
        if self.m_DiscardPredictions:
            return None
        return self.m_Predictions


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
                pred= Utils.maxIndex(a0)
                if a0[int(pred)] <= 0:
                    pred= Utils.missingValue()
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
            classMissing=copy.deepcopy(instance)
            classMissing.setDataset(instance.dataset())
            #TODO
            # if isinstance(a0,InputMappedClassifier)
            # else:
            classMissing.setClassMissing()
            # print("isMiss: ", instance.value(5))

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
            self.m_SumSqrClass+=instance.weight()*instance.classValue()*instance.classValue()
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
                self.m_SumKBInfo+= (Utils.log2(predictedProb) - Utils.log2(priorProb)) * instance.weight()
            else:
                self.m_SumKBInfo-= (Utils.log2(1 - predictedProb) - Utils.log2(1 - priorProb)) * instance.weight()
            self.m_SumSchemeEntropy-= Utils.log2(predictedProb) * instance.weight()
            self.m_SumPriorEntropy-= Utils.log2(priorProb) * instance.weight()
            self.updateNumericScores(predictedDistribution,self.makeDistribution(instance.classValue()),instance.weight())
            indices= Utils.stableSort(predictedDistribution)
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

    def toMatrixString(self,title="=== Confusion Matrix ===\n"):
        text=""
        IDChars =['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n','o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        fractional=False
        if not self.m_ClassIsNominal:
            raise Exception("Evaluation: No confusion matrix possible!")
        maxval=0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                current=self.m_ConfusionMatrix[i][j]
                if current < 0:
                    current*=-10
                if current > maxval:
                    maxval=current
                fract=current-np.rint(current)
                if fract == 0:
                    fract=float('inf')
                if not fractional and math.log(fract)/math.log(10)>=-2:
                    fractional=True
        try:
            IDWidth=1+max(int(math.log(maxval)/math.log(10)+3 if fractional else 0),
                          int(math.log(self.m_NumClasses)/math.log(len(IDChars))))
        except ValueError:
            if maxval == 0:
                IDWidth=1+int(math.log(self.m_NumClasses)/math.log(len(IDChars)))
            else:
                raise ValueError
        text+=title+'\n'
        for i in range(self.m_NumClasses):
            if fractional:
                text+=" "+self.num2ShortID(i,IDChars,IDWidth-3)+"   "
            else:
                text+=" "+self.num2ShortID(i,IDChars,IDWidth)
        text+="<-- classified as\n"
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                text+=" " + Utils.doubleToString(self.m_ConfusionMatrix[i][j], IDWidth, 2 if fractional else 0)
            text+=" | "+self.num2ShortID(i,IDChars,IDWidth)+" = "+self.m_ClassNames[i]+"\n"
        return text

    def toClassDetailsString(self,title:str="=== Detailed Accuracy By Class ===\n"):
        if not self.m_ClassIsNominal:
            raise Exception("Evaluation: No per class statistics possible!")
        displayTP = "tp rate" in self.m_metricsToDisplay
        displayFP ="fp rate" in self.m_metricsToDisplay
        displayP = "precision" in self.m_metricsToDisplay
        displayR = "recall" in self.m_metricsToDisplay
        displayFM = "f-measure" in self.m_metricsToDisplay
        displayMCC ="mcc" in self.m_metricsToDisplay
        displayROC = "roc area" in self.m_metricsToDisplay
        displayPRC ="prc area" in self.m_metricsToDisplay

        text=title+"\n                 "\
        +  ("TP Rate     "   if displayTP else "")   +   ("FP Rate     " if displayFP else "")\
        +  ("Precision   "   if displayP else "")    +   ("Recall      " if displayR else "")\
        +  ("F-Measure   "   if displayFM else "")   +   ("MCC         " if displayMCC else "")\
        +  ("ROC Area    "   if displayROC else "")  +   ("PRC Area    " if displayPRC else "")\
        +  "Class\n"
        for i in range(self.m_NumClasses):
            text+="                 "
            if displayTP:
                tpr=self.truePositiveRate(i)
                if Utils.isMissingValue(tpr):
                    text+="?           "
                else:
                    text+="{:<12.3f}".format(tpr)
            if displayFP:
                fpr=self.falsePositiveRate(i)
                if Utils.isMissingValue(fpr):
                    text+="?           "
                else:
                    text+="{:<12.3f}".format(fpr)
            if displayP:
                p=self.precision(i)
                if Utils.isMissingValue(p):
                    text+="?           "
                else:
                    text+="{:<12.3f}".format(p)
            if displayR:
                r=self.recall(i)
                if Utils.isMissingValue(r):
                    text+="?           "
                else:
                    text+="{:<12.3f}".format(r)
            if displayFM:
                fm=self.fMeasure(i)
                if Utils.isMissingValue(fm):
                    text+="?           "
                else:
                    text+="{:<12.3f}".format(fm)
            if displayMCC:
                mat=self.matthewsCorrelationCoefficient(i)
                if Utils.isMissingValue(mat):
                    text+="?           "
                else:
                    text+="{:<12.3f}".format(mat)
            if displayROC:
                rocVal=self.areaUnderROC(i)
                if Utils.isMissingValue(rocVal):
                    text += "?           "
                else:
                    text+="{:<12.3f}".format(rocVal)
            if displayPRC:
                prcVal=self.areaUnderPRC(i)
                if Utils.isMissingValue(prcVal):
                    text += "?           "
                else:
                    text+="{:<12.3f}".format(prcVal)
            text+=self.m_ClassNames[i]+"\n"
        text+="Weighted Avg.    "

        if displayTP:
            wtpr=self.weightedTruePositiveRate()
            if Utils.isMissingValue(wtpr):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wtpr)
        if displayFP:
            wfpr=self.weightedFalsePositiveRate()
            if Utils.isMissingValue(wfpr):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wfpr)
        if displayP:
            wp=self.weightedPrecision()
            if Utils.isMissingValue(wp):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wp)
        if displayR:
            wr=self.weightedRecall()
            if Utils.isMissingValue(wr):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wr)
        if displayFM:
            wf=self.weightedFMeasure()
            if Utils.isMissingValue(wf):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wf)
        if displayMCC:
            wmc=self.weightedMatthewsCorrelation()
            if Utils.isMissingValue(wmc):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wmc)
        if displayROC:
            wroc=self.weightedAreaUnderROC()
            if Utils.isMissingValue(wroc):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wroc)
        if displayPRC:
            wprc=self.weightedAreaUnderPRC()
            if Utils.isMissingValue(wprc):
                text+="?           "
            else:
                text+="{:<12.3f}".format(wprc)
        text+="\n"
        return text

    def areaUnderPRC(self,classIndex:int):
        if self.m_Predictions is None:
            return Utils.missingValue()
        else:
            tc=ThresholdCurve()
            result=tc.getCurve(self.m_Predictions,classIndex)
            return ThresholdCurve.getPRCArea(result)

    def areaUnderROC(self,classIndex:int):
        if self.m_Predictions is None:
            return Utils.missingValue()
        else:
            tc=ThresholdCurve()
            result=tc.getCurve(self.m_Predictions,classIndex)
            return ThresholdCurve.getROCArea(result)

    def matthewsCorrelationCoefficient(self,classIndex:int):
        numTP=self.numTruePositives(classIndex)
        numTN=self.numTrueNegatives(classIndex)
        numFP=self.numFalsePositives(classIndex)
        numFN=self.numFalseNegatives(classIndex)
        n=numTP*numTN-numFP*numFN
        d=(numTP+numFP)*(numTP+numFN)*(numTN+numFP)*(numTN+numFN)
        d=math.sqrt(d)
        return Utils.division(n, d)

    def numTruePositives(self,classIndex:int):
        correct=0
        for j in range(self.m_NumClasses):
            if j == classIndex:
                correct+=self.m_ConfusionMatrix[classIndex][j]
        return correct

    def numFalseNegatives(self,classIndex:int):
        incorrect=0
        for i in range(self.m_NumClasses):
            if i == classIndex:
                for j in range(self.m_NumClasses):
                    if j != classIndex:
                        incorrect+=self.m_ConfusionMatrix[i][j]
        return incorrect

    def numFalsePositives(self,classIndex:int):
        incorrect=0
        for i in range(self.m_NumClasses):
            if i != classIndex:
                for j in range(self.m_NumClasses):
                    if j == classIndex:
                        incorrect+=self.m_ConfusionMatrix[i][j]
        return incorrect

    def numTrueNegatives(self,classIndex:int):
        correct=0
        for i in range(self.m_NumClasses):
            if i != classIndex:
                for j in range(self.m_NumClasses):
                    if j != classIndex:
                        correct+=self.m_ConfusionMatrix[i][j]
        return correct

    def fMeasure(self,classIndex:int):
        precision=self.precision(classIndex)
        recall=self.recall(classIndex)
        if precision == 0 and recall == 0:
            return 0
        return 2*precision*recall/(precision+recall)

    def recall(self,classIndex:int):
        return self.truePositiveRate(classIndex)

    def precision(self,classIndex:int):
        correct=total=0
        for i in range(self.m_NumClasses):
            if i == classIndex:
                correct+=self.m_ConfusionMatrix[i][classIndex]
            total+=self.m_ConfusionMatrix[i][classIndex]
        return Utils.division(correct, total)

    def truePositiveRate(self,classIndex:int):
        correct=total=0
        for j in range(self.m_NumClasses):
            if j == classIndex:
                correct+=self.m_ConfusionMatrix[classIndex][j]
            total+=self.m_ConfusionMatrix[classIndex][j]
        return Utils.division(correct, total)

    def falsePositiveRate(self,classIndex:int):
        incorrect=total=0
        for i in range(self.m_NumClasses):
            if i != classIndex:
                for j in range(self.m_NumClasses):
                    if j == classIndex:
                        incorrect+=self.m_ConfusionMatrix[i][j]
                    total+=self.m_ConfusionMatrix[i][j]
        return Utils.division(incorrect, total)

    def weightedTruePositiveRate(self):
        classCounts=[0]*self.m_NumClasses
        classCountSum=0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i]+=self.m_ConfusionMatrix[i][j]
            classCountSum+=classCounts[i]
        truePosTotal=0
        for i in range(self.m_NumClasses):
            temp=self.truePositiveRate(i)
            if classCounts[i]>0:
                truePosTotal+=temp*classCounts[i]
        return Utils.division(truePosTotal, classCountSum)

    def weightedFalsePositiveRate(self):
        classCounts=[0]*self.m_NumClasses
        classCountSum=0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i]+=self.m_ConfusionMatrix[i][j]
            classCountSum+=classCounts[i]
        falsePosTotal=0
        for i in range(self.m_NumClasses):
            temp=self.falsePositiveRate(i)
            if classCounts[i]>0:
                falsePosTotal+=temp*classCounts[i]
        return Utils.division(falsePosTotal, classCountSum)

    def weightedPrecision(self):
        classCounts=[0]*self.m_NumClasses
        classCountSum=0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i]+=self.m_ConfusionMatrix[i][j]
            classCountSum+=classCounts[i]
        precisionTotal=0
        for i in range(self.m_NumClasses):
            temp=self.precision(i)
            if classCounts[i]>0:
                precisionTotal+=temp*classCounts[i]
        return Utils.division(precisionTotal, classCountSum)

    def weightedRecall(self):
        return self.weightedTruePositiveRate()

    def weightedFMeasure(self):
        classCounts = [0] * self.m_NumClasses
        classCountSum = 0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i] += self.m_ConfusionMatrix[i][j]
            classCountSum += classCounts[i]
        fMeasureTotal = 0
        for i in range(self.m_NumClasses):
            temp = self.fMeasure(i)
            if classCounts[i] > 0:
                fMeasureTotal += temp * classCounts[i]
        return Utils.division(fMeasureTotal, classCountSum)

    def weightedMatthewsCorrelation(self):
        classCounts = [0] * self.m_NumClasses
        classCountSum = 0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i] += self.m_ConfusionMatrix[i][j]
            classCountSum += classCounts[i]
        mccTotal = 0
        for i in range(self.m_NumClasses):
            temp = self.matthewsCorrelationCoefficient(i)
            if classCounts[i] > 0:
                mccTotal += temp * classCounts[i]
        return Utils.division(mccTotal, classCountSum)

    def weightedAreaUnderROC(self):
        classCounts = [0] * self.m_NumClasses
        classCountSum = 0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i] += self.m_ConfusionMatrix[i][j]
            classCountSum += classCounts[i]
        aucTotal = 0
        for i in range(self.m_NumClasses):
            temp = self.areaUnderROC(i)
            if classCounts[i] > 0:
                aucTotal += temp * classCounts[i]
        return Utils.division(aucTotal, classCountSum)

    def weightedAreaUnderPRC(self):
        classCounts = [0] * self.m_NumClasses
        classCountSum = 0
        for i in range(self.m_NumClasses):
            for j in range(self.m_NumClasses):
                classCounts[i] += self.m_ConfusionMatrix[i][j]
            classCountSum += classCounts[i]
        auprcTotal = 0
        for i in range(self.m_NumClasses):
            temp = self.areaUnderPRC(i)
            if classCounts[i] > 0:
                auprcTotal += temp * classCounts[i]
        return Utils.division(auprcTotal, classCountSum)

    def num2ShortID(self,num:int,IDChars:List[str],IDWidth:int):
        ID=[]
        i=0
        for i in range(IDWidth-1,-1,-1):
            ID.append(IDChars[num%len(IDChars)])
            num=num/len(IDChars)-1
            if num <0 :
                break
        for i in range(i-1,-1,-1):
            ID.insert(0," ")
        return "".join(ID)

    def toSummaryString(self,printComplexityStatistics:bool,title:str="=== Summary ===\n"):
        if printComplexityStatistics and self.m_NoPriors:
            printComplexityStatistics=False
        text=title+'\n'
        if self.m_WithClass > 0:
            if self.m_ClassIsNominal:
                displayCorrect="correct" in self.m_metricsToDisplay
                displayIncorrect="incorrect" in self.m_metricsToDisplay
                displayKappa="kappa" in self.m_metricsToDisplay


                if displayCorrect:
                    text+="Correctly Classified Instances     "
                    text+= Utils.doubleToString(self.correct(), 12, 4) + "     " + Utils.doubleToString(self.pctCorrect(), 12, 4) + " %\n"
                if displayIncorrect:
                    text+="Incorrectly Classified Instances   "
                    text+= Utils.doubleToString(self.incorrect(), 12, 4) + "     " + Utils.doubleToString(self.pctIncorrect(), 12, 4) + " %\n"
                if displayKappa:
                    text+="Kappa statistic                    "
                    text+= Utils.doubleToString(self.kappa(), 12, 4) + "\n"
                if printComplexityStatistics:
                    displayKBRelative="kb relative" in self.m_metricsToDisplay
                    displayKBInfo="kb information" in self.m_metricsToDisplay
                    if displayKBRelative:
                        text+="K&B Relative Info Score            "
                        text+= Utils.doubleToString(self.KBRelativeInformation(), 12, 4) + " %\n"
                    if displayKBInfo:
                        text+="K&B Information Score              "
                        text+= Utils.doubleToString(self.KBInformation(), 12, 4) + " bits"
                        text+= Utils.doubleToString(self.KBMeanInformation(), 12, 4) + " bits/instance\n"
                #if self.m_pluginMetrics != null:
            else:
                displayCorrelation="correlation" in self.m_metricsToDisplay
                if displayCorrelation:
                    text+="Correlation coefficient            "
                    text+= Utils.doubleToString(self.correlationCoefficient(), 12, 4) + "\n"
                # if self.m_pluginMetrics != null:
            if printComplexityStatistics and self.m_ComplexityStatisticsAvailable:
                displayComplexityOrder0="complexity 0" in self.m_metricsToDisplay
                displayComplexityScheme="complexity scheme" in self.m_metricsToDisplay
                displayComplexityImprovement="complexity improvement" in self.m_metricsToDisplay
                if displayComplexityOrder0:
                    text+="Class complexity | order 0         "
                    text+= Utils.doubleToString(self.SFPriorEntropy(), 12, 4) + " bits"
                    text+= Utils.doubleToString(self.SFMeanPriorEntropy(), 12, 4) + " bits/instance\n"
                if displayComplexityScheme:
                    text+="Class complexity | scheme          "
                    text+= Utils.doubleToString(self.SFSchemeEntropy(), 12, 4) + " bits"
                    text+= Utils.doubleToString(self.SFMeanSchemeEntropy(), 12, 4) + " bits/instance\n"
                if displayComplexityImprovement:
                    text+="Complexity improvement     (Sf)    "
                    text+= Utils.doubleToString(self.SFEntropyGain(), 12, 4) + " bits"
                    text+= Utils.doubleToString(self.SFMeanEntropyGain(), 12, 4) + " bits/instance\n"
            displayMAE = "mae" in self.m_metricsToDisplay
            displayRMSE = "rmse" in self.m_metricsToDisplay
            displayRAE = "rae" in self.m_metricsToDisplay
            displayRRSE = "rrse" in self.m_metricsToDisplay
            if displayMAE:
                text+="Mean absolute error                "
                text+= Utils.doubleToString(self.meanAbsoluteError(), 12, 4) + "\n"
            if displayRMSE:
                text+="Root mean squared error            "
                text+= Utils.doubleToString(self.rootMeanSquaredError(), 12, 4) + "\n"
            if not self.m_NoPriors:
                if displayRAE:
                    text+="Relative absolute error            "
                    text+= Utils.doubleToString(self.relativeAbsoluteError(), 12, 4) + " %\n"
                if displayRRSE:
                    text+="Root relative squared error        "
                    text+= Utils.doubleToString(self.rootRelativeSquaredError(), 12, 4) + " %\n"
            if self.m_CoverageStatisticsAvailable:
                displayCoverage="coverage" in self.m_metricsToDisplay
                displayRegionSize="region size" in self.m_metricsToDisplay
                if displayCoverage:
                    text+="Coverage of cases " + Utils.doubleToString(self.m_ConfLevel, 4, 2) + " level)     "
                    text+= Utils.doubleToString(self.coverageOfTestCasesByPredictedRegions(), 12, 4) + " %\n"
                if not self.m_NoPriors:
                    if displayRegionSize:
                        text+="Mean rel. region size (" + Utils.doubleToString(self.m_ConfLevel, 4, 2) + " level) "
                        text+= Utils.doubleToString(self.sizeOfPredictedRegions(), 12, 4) + " %\n"
        if Utils.gr(self.unclassified(), 0):
            text+="UnClassified Instances             "
            text+= Utils.doubleToString(self.unclassified(), 12, 4) + "     " + Utils.doubleToString(self.pctUnclassified(), 12, 4) + " %\n"
        text+="Total Number of Instances          "
        text+= Utils.doubleToString(self.m_WithClass, 12, 4) + "\n"
        if self.m_MissingClass>0:
            text+="Ignored Class Unknown Instances            "
            text+= Utils.doubleToString(self.m_MissingClass, 12, 4) + "\n"
        return text

    def unclassified(self):
        return self.m_Unclassified

    def pctUnclassified(self):
        return 100*self.m_Unclassified/self.m_WithClass

    def coverageOfTestCasesByPredictedRegions(self):
        if not self.m_CoverageStatisticsAvailable:
            return float('nan')
        return 100*self.m_TotalCoverage/self.m_WithClass

    def sizeOfPredictedRegions(self):
        if self.m_NoPriors or not self.m_CoverageStatisticsAvailable:
            return float('nan')
        return 100*self.m_TotalSizeOfRegions/self.m_WithClass

    def withClass(self):
        return self.m_WithClass

    def rootMeanSquaredError(self):
        return math.sqrt(self.m_SumSqrErr/(self.m_WithClass-self.m_Unclassified))

    def rootMeanPriorSquaredError(self):
        if self.m_NoPriors:
            return float('nan')
        return math.sqrt(self.m_SumPriorSqrErr/self.m_WithClass)

    def relativeAbsoluteError(self):
        if self.m_NoPriors:
            return float('nan')
        return 100*self.meanAbsoluteError()/self.meanPriorAbsoluteError()

    def rootRelativeSquaredError(self):
        if self.m_NoPriors:
            return float('nan')
        return 100*self.rootMeanSquaredError()/self.rootMeanPriorSquaredError()

    def meanAbsoluteError(self):
        return self.m_SumAbsErr/(self.m_WithClass-self.m_Unclassified)

    def meanPriorAbsoluteError(self):
        if self.m_NoPriors:
            return float('nan')
        return self.m_SumPriorAbsErr/self.m_WithClass


    def SFPriorEntropy(self):
        if self.m_NoPriors or not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return self.m_SumPriorEntropy

    def SFMeanPriorEntropy(self):
        if self.m_NoPriors or not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return self.m_SumPriorEntropy/self.m_WithClass

    def SFSchemeEntropy(self):
        if not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return self.m_SumSchemeEntropy

    def SFMeanSchemeEntropy(self):
        if not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return self.m_SumSchemeEntropy/(self.m_WithClass-self.m_Unclassified)

    def SFEntropyGain(self):
        if self.m_NoPriors or not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return self.m_SumPriorEntropy-self.m_SumSchemeEntropy

    def SFMeanEntropyGain(self):
        if self.m_NoPriors or not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return (self.m_SumPriorEntropy-self.m_SumSchemeEntropy)/(self.m_WithClass-self.m_Unclassified)

    def correlationCoefficient(self):
        if self.m_ClassIsNominal:
            raise Exception("Can't compute correlation coefficient: "+ "class is nominal!")
        correlation=0
        varActual=self.m_SumSqrClass-self.m_SumClass*self.m_SumClass/(self.m_WithClass-self.m_Unclassified)
        varPredicted=self.m_SumSqrPredicted-self.m_SumPredicted*self.m_SumPredicted/(self.m_WithClass-self.m_Unclassified)
        varProd=self.m_SumClassPredicted-self.m_SumClass*self.m_SumClass/(self.m_WithClass-self.m_Unclassified)
        if varActual*varPredicted<=0:
            correlation=0
        else:
            correlation=varProd/math.sqrt(varActual*varPredicted)
        return correlation

    def KBInformation(self):
        if not self.m_ClassIsNominal:
            raise Exception("Can't compute K&B Info score: " + "class numeric!")
        if self.m_NoPriors:
            return float('nan')
        return self.m_SumKBInfo

    def KBRelativeInformation(self):
        if not self.m_ClassIsNominal:
            raise Exception("Can't compute K&B Info score: " + "class numeric!")
        if self.m_NoPriors:
            return float('nan')
        return 100*self.KBMeanInformation()/self.priorEntropy()

    def priorEntropy(self):
        return self.SFMeanPriorEntropy()

    def SFMeanPriorEntropy(self):
        if self.m_NoPriors or not self.m_ComplexityStatisticsAvailable:
            return float('nan')
        return self.m_SumPriorEntropy/self.m_WithClass

    def KBMeanInformation(self):
        if not self.m_ClassIsNominal:
            raise Exception("Can't compute K&B Info score: class numeric!")
        if self.m_NoPriors:
            return float('nan')
        return self.m_SumKBInfo/(self.m_WithClass-self.m_Unclassified)

    def correct(self):
        return self.m_Correct

    def pctCorrect(self):
        return 100*self.m_Correct/self.m_WithClass

    def incorrect(self):
        return self.m_Incorrect

    def pctIncorrect(self):
        return 100*self.m_Incorrect/self.m_WithClass

    def kappa(self):
        sumRows=[0]*len(self.m_ConfusionMatrix)
        sumColumns=[0]*len(self.m_ConfusionMatrix)
        sumOfWeights=0
        for i in range(len(self.m_ConfusionMatrix)):
            for j in range(len(self.m_ConfusionMatrix)):
                sumRows[i]+=self.m_ConfusionMatrix[i][j]
                sumColumns[j]+=self.m_ConfusionMatrix[i][j]
                sumOfWeights+=self.m_ConfusionMatrix[i][j]
        correct=chanceAgreement=0
        for i in range(len(self.m_ConfusionMatrix)):
            chanceAgreement+=sumRows[i]*sumColumns[i]
            correct+=self.m_ConfusionMatrix[i][i]
        chanceAgreement/=sumOfWeights*sumOfWeights
        correct/=sumOfWeights
        if chanceAgreement <1:
            return (correct-chanceAgreement)/(1-chanceAgreement)
        else:
            return 1

    @classmethod
    def getAllEvaluationMetricNames(cls):
        allEvals=[]     #type:List[str]
        for s in cls.BUILT_IN_EVAL_METRICS:
            allEvals.append(s)
        return allEvals





