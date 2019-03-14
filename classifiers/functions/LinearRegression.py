from typing import *
from classifiers.AbstractClassifier import AbstractClassifier
from Instances import Instances,Instance
from filters.Filter import Filter
from filters.attribute.ReplaceMissingValues import ReplaceMissingValues
from filters.attribute.NominalToBinary import NominalToBinary
import classifiers.evaluation.RegressionAnalysis as RegressionAnalysis
from Tag import Tag
from Capabilities import Capabilities,CapabilityEnum
from Utils import Utils
import math
import numpy as np

class LinearRegression(AbstractClassifier):
    SELECTION_M5=0      #default
    SELECTION_NONE=1
    SELECTION_GREEDY=2
    TAGS_SELECTION=[Tag(SELECTION_NONE,"No attribute selection"),Tag((SELECTION_M5,"M5 method"),)]
    def __init__(self):
        super().__init__()
        self.m_Coefficients=None    #type:List[float]
        self.m_SelectedAttributes=None      #type:List[bool]
        self.m_TransformedData=None     #type:Instances
        self.m_MissingFilter=None       #type:ReplaceMissingValues
        self.m_TransformFilter=None         #type:NominalToBinary
        self.m_ClassStdDev=0
        self.m_ClassMean=0
        self.m_ClassIndex=0
        self.m_Means=None   #type:List[float]
        self.m_StdDevs=None     #type:List[float]
        self.outputAdditionalStats=False
        self.AttributeSelectionMethod=0
        self.EliminateColinearAttributes=True
        self.m_checksTurnedOff=False
        self.Ridge=1e-8
        self.Minimal=False
        self.m_ModelBuilt=False
        self.m_isZeroR=False
        self.m_df=0
        self.m_RSquared=0
        self.m_RSquaredAdj=0
        self.m_FStat=0
        self.m_StdErrorOfCoef=None  #type:List[float]
        self.m_TStats=None      #type:List[float]
        self.numDecimalPlaces=4

    def __str__(self):
        if not self.m_ModelBuilt:
            return "Linear Regression: No model built yet."
        if self.Minimal:
            return "Linear Regression: Model built."
        text=""
        column=0
        first=True
        text+="\nLinear Regression Model\n\n"
        text+=self.m_TransformedData.classAttribute().name()+" =\n\n"
        for i in range(self.m_TransformedData.numAttributes()):
            if i != self.m_ClassIndex and self.m_SelectedAttributes[i]:
                if not first:
                    text+=" +\n"
                else:
                    first=False
                text+=Utils.doubleToString(self.m_Coefficients[column],12,self.numDecimalPlaces)+" * "
                text+=self.m_TransformedData.attribute(i).name()
                column+=1
        text+=" +\n"+ Utils.doubleToString(self.m_Coefficients[column], 12, self.numDecimalPlaces)
        if self.outputAdditionalStats:
            maxAttLength=0
            for i in range(self.m_TransformedData.numAttributes()):
                if i != self.m_ClassIndex and self.m_SelectedAttributes[i]:
                    if len(self.m_TransformedData.attribute(i).name()) > maxAttLength:
                        maxAttLength=len(self.m_TransformedData.attribute(i).name())
            maxAttLength+=3
            if maxAttLength < len("Variable")+3:
                maxAttLength=len("Variable")+3
            text+="\n\nRegression Analysis:\n\n"\
                  + Utils.padRight("Variable", maxAttLength)\
                  + "  Coefficient     SE of Coef        t-Stat"
            column=0
            for i in range(self.m_TransformedData.numAttributes()):
                if i != self.m_ClassIndex and self.m_SelectedAttributes[i]:
                    text+="\n" + Utils.padRight(self.m_TransformedData.attribute(i).name(), maxAttLength)
                    text+=Utils.doubleToString(self.m_Coefficients[column],12,self.numDecimalPlaces)
                    text+="   "+ Utils.doubleToString(self.m_StdErrorOfCoef[column], 12,self.numDecimalPlaces)
                    text+="   "+ Utils.doubleToString(self.m_TStats[column], 12, self.numDecimalPlaces)
                    column+=1
            text+=Utils.padRight("\nconst", maxAttLength + 1)+ Utils.doubleToString(self.m_Coefficients[column], 12, self.numDecimalPlaces)
            text+="   "+ Utils.doubleToString(self.m_StdErrorOfCoef[column], 12,self.numDecimalPlaces)
            text+="   "+ Utils.doubleToString(self.m_TStats[column], 12, self.numDecimalPlaces)
            text+="\n\nDegrees of freedom = " + str(self.m_df)
            text+="\nR^2 value = "+ Utils.doubleToString(self.m_RSquared, self.numDecimalPlaces)
            text+="\nAdjusted R^2 = "+ Utils.doubleToString(self.m_RSquaredAdj, 5)
            text+="\nF-statistic = "+ Utils.doubleToString(self.m_FStat, self.numDecimalPlaces)
        return text


    def getCapabilities(self):
        result=super().getCapabilities()
        result.disableAll()
        result.enable(CapabilityEnum.NOMINAL_ATTRIBUTES)
        result.enable(CapabilityEnum.NUMERIC_ATTRIBUTES)
        result.enable(CapabilityEnum.DATE_ATTRIBUTES)
        result.enable(CapabilityEnum.MISSING_VALUES)
        result.enable(CapabilityEnum.NUMERIC_CLASS)
        result.enable(CapabilityEnum.DATE_CLASS)
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)
        return result

    def buildClassifier(self,data:Instances):
        self.m_ModelBuilt=False
        self.m_isZeroR=False
        if data.numInstances() == 1:
            self.m_Coefficients=[data.instance(0).classValue()]
            self.m_SelectedAttributes=[False]*data.numAttributes()
            self.m_isZeroR=True
            return
        if not self.m_checksTurnedOff:
            self.getCapabilities().testWithFail(data)
            if self.outputAdditionalStats:
                ok=True
                for i in range(data.numInstances()):
                    if data.instance(i).weight() != 1:
                        ok=False
                        break
                if not ok:
                    raise Exception("Can only compute additional statistics on unweighted data")
            data=Instances(data)
            data.deleteWithMissingClass()
            self.m_TransformFilter=NominalToBinary()
            self.m_TransformFilter.setInputFormat(data)
            data=Filter.useFilter(data,self.m_TransformFilter)
            self.m_MissingFilter=ReplaceMissingValues()
            self.m_MissingFilter.setInputFormat(data)
            data=Filter.useFilter(data,self.m_MissingFilter)
            data.deleteWithMissingClass()
        else:
            self.m_TransformFilter=None
            self.m_MissingFilter=None
        self.m_ClassIndex=data.classIndex()
        self.m_TransformedData=data
        self.m_Coefficients=None
        self.m_SelectedAttributes=[False]*data.numAttributes()
        self.m_Means=[0]*data.numAttributes()
        self.m_StdDevs=[0]*data.numAttributes()
        for j in range(data.numAttributes()):
            if j != self.m_ClassIndex:
                self.m_SelectedAttributes[j]=True
                self.m_Means[j]=data.meanOrMode(j)
                self.m_StdDevs[j]=math.sqrt(data.variance(j))
                if self.m_StdDevs[j] == 0:
                    self.m_SelectedAttributes[j]=False
        self.m_ClassStdDev=math.sqrt(data.variance(self.m_TransformedData.classIndex()))
        self.m_ClassMean=data.meanOrMode(self.m_TransformedData.classIndex())
        self.findBestModel()
        if self.outputAdditionalStats:
            k=1
            for i in range(data.numAttributes()):
                if i != data.classIndex():
                    if self.m_SelectedAttributes[i]:
                        k+=1
            self.m_df=self.m_TransformedData.numInstances()-k
            se= self.calculateSE(self.m_SelectedAttributes,self.m_Coefficients)
            self.m_RSquared=RegressionAnalysis.calculateRSquared(self.m_TransformedData,se)
            self.m_RSquaredAdj=RegressionAnalysis.calculateAdjRSquared(self.m_RSquared,self.m_TransformedData.numInstances(),k)
            self.m_FStat=RegressionAnalysis.calculateFStat(self.m_RSquared,self.m_TransformedData.numInstances(),k)
            self.m_StdErrorOfCoef=RegressionAnalysis.calculateStdErrorOfCoef(self.m_TransformedData,
                                                                             self.m_SelectedAttributes,se,
                                                                             self.m_TransformedData.numInstances(),k)
            self.m_TStats=RegressionAnalysis.calculateTStats(self.m_Coefficients,self.m_StdErrorOfCoef,k)
        if self.Minimal:
            self.m_TransformedData=None
            self.m_Means=None
            self.m_StdDevs=None
        else:
            self.m_TransformedData=Instances(data,0)
        self.m_ModelBuilt=True

    def classifyInstance(self,instance:Instance):
        transformedInstance=instance
        if not self.m_checksTurnedOff and not self.m_isZeroR:
            self.m_TransformFilter.input(transformedInstance)
            self.m_TransformFilter.batchFinished()
            transformedInstance=self.m_TransformFilter.output()
            self.m_MissingFilter.input(transformedInstance)
            self.m_MissingFilter.batchFinished()
            transformedInstance=self.m_MissingFilter.output()
        return self.regressionPrediction(transformedInstance,self.m_SelectedAttributes,self.m_Coefficients)



    def findBestModel(self):
        numInstances=self.m_TransformedData.numInstances()
        self.m_Coefficients=self.doRegression(self.m_SelectedAttributes)
        while self.EliminateColinearAttributes and self.deselectColinearAttributes(self.m_SelectedAttributes,self.m_Coefficients):
            self.m_Coefficients=self.doRegression(self.m_SelectedAttributes)
        numAttributes=1
        for m_SelectedAttribute in self.m_SelectedAttributes:
            if m_SelectedAttribute:
                numAttributes+=1
        fullMSE=self.calculateSE(self.m_SelectedAttributes,self.m_Coefficients)
        akaike=(numInstances-numAttributes)+2*numAttributes
        currentNumAttributes=numAttributes
        improved = True
        if self.AttributeSelectionMethod == self.SELECTION_GREEDY:
            while improved:
                currentSelected=self.m_SelectedAttributes[:]
                improved=False
                currentNumAttributes-=1
                for i in range(len(self.m_SelectedAttributes)):
                    if currentSelected[i]:
                        currentSelected[i]=False
                        currentCoeffs=self.doRegression(currentSelected)
                        currentMSE=self.calculateSE(currentSelected,currentCoeffs)
                        currentAkaike=currentMSE/fullMSE*(numInstances-numAttributes)+2*currentNumAttributes
                        if currentAkaike < akaike:
                            improved=True
                            akaike=currentAkaike
                            self.m_SelectedAttributes=currentSelected[:]
                            self.m_Coefficients=currentCoeffs
                        currentSelected[i]=True
        elif self.AttributeSelectionMethod == self.SELECTION_M5:
            while improved:
                improved=False
                currentNumAttributes-=1
                minSC=0
                minAttr=-1
                coeff=0
                for i in range(len(self.m_SelectedAttributes)):
                    if self.m_SelectedAttributes[i]:
                        SC=math.fabs(self.m_Coefficients[coeff]*self.m_StdDevs[i]/self.m_ClassStdDev)
                        if coeff == 0 or SC < minSC:
                            minSC=SC
                            minAttr=i
                        coeff+=1
                if minAttr >= 0:
                    self.m_SelectedAttributes[minAttr]=False
                    currentCoeffs=self.doRegression(self.m_SelectedAttributes)
                    currentMSE=self.calculateSE(self.m_SelectedAttributes,currentCoeffs)
                    currentAkaike=currentMSE/fullMSE*(numInstances-numAttributes)+2*currentNumAttributes
                    if currentAkaike < akaike:
                        improved=True
                        akaike=currentAkaike
                        self.m_Coefficients=currentCoeffs
                    else:
                        self.m_SelectedAttributes[minAttr]=True


    def calculateSE(self,selectedAttributes:List[bool],coefficients:List[float]):
        mse=0
        for i in range(self.m_TransformedData.numInstances()):
            prediction=self.regressionPrediction(self.m_TransformedData.instance(i),selectedAttributes,coefficients)
            error=prediction-self.m_TransformedData.instance(i).classValue()
            mse+=error*error
        return mse

    def regressionPrediction(self,transformedInstance:Instance,selectedAttributes:List[bool],coefficients:List[float]):
        result=0
        column=0
        for j in range(transformedInstance.numAttributes()):
            if self.m_ClassIndex != j and selectedAttributes[j]:
                result+=coefficients[column]*transformedInstance.value(j)
                column+=1
        result+=coefficients[column]
        return result

    def deselectColinearAttributes(self,selectedAttributes:List[bool],coefficients:List[float]):
        maxSC=1.5
        maxAttr=-1
        coeff=0
        for i in range(len(selectedAttributes)):
            if selectedAttributes[i]:
                SC=math.fabs(coefficients[coeff]*self.m_StdDevs[i]/self.m_ClassStdDev)
                if SC > maxSC:
                    maxSC=SC
                    maxAttr=i
                coeff+=1
        if maxAttr >= 0:
            selectedAttributes[maxAttr]=False
            return True
        return False

    def doRegression(self,selectedAttributes:List[bool])->List:
        numAttributes=0
        for selectedAttribute in selectedAttributes:
            if selectedAttribute:
                numAttributes+=1
        coefficients=[0]*(numAttributes+1)
        if numAttributes > 0:
            independentTransposed=np.zeros((numAttributes,self.m_TransformedData.numInstances()))
            dependent=np.zeros(self.m_TransformedData.numInstances())
            for i in range(self.m_TransformedData.numInstances()):
                inst=self.m_TransformedData.instance(i)
                sqrt_weight=math.sqrt(inst.weight())
                index=0
                for j in range(self.m_TransformedData.numAttributes()):
                    if j == self.m_ClassIndex:
                        dependent[i]=inst.classValue()*sqrt_weight
                    else:
                        if selectedAttributes[j]:
                            value=inst.value(j)-self.m_Means[j]
                            if not self.m_checksTurnedOff:
                                value/=self.m_StdDevs[j]
                            independentTransposed[index][i]=value*sqrt_weight
                            index+=1

            aTy=np.dot(independentTransposed,dependent)
            aTa=np.around(np.dot(independentTransposed,independentTransposed.T),2)
            ridge=self.getRidge()
            for i in range(numAttributes):
                aTa[i][i]+=ridge
            coeffsWithoutIntercept=np.dot(aTy,np.linalg.pinv(aTa))
            if len(coeffsWithoutIntercept.shape) > 1:
                coefficients=coeffsWithoutIntercept[0].copy()
            else:
                coefficients=coeffsWithoutIntercept.copy()
        coefficients[numAttributes]=self.m_ClassMean
        column=0
        for i in range(self.m_TransformedData.numAttributes()):
            if i != self.m_TransformedData.classIndex() and selectedAttributes[i]:
                if not self.m_checksTurnedOff:
                    coefficients[column]/=self.m_StdDevs[i]
                coefficients[-1]-=coefficients[column]*self.m_Means[i]
                column+=1
        return coefficients


    def getRidge(self):
        return self.Ridge