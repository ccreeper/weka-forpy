from typing import *

from AbstractPlotInstances import AbstractPlotInstances
from Attributes import Attribute
from Instances import Instances, Instance
from Utils import Utils
from classifiers.Classifier import Classifier
from classifiers.evaluation.Evaluation import Evaluation
from gui.classifier.Plot2D import Plot2D
from PlotData2D import PlotData2D
import copy


class ClassifierErrorsPlotInstances(AbstractPlotInstances):
    def __init__(self):
        super().__init__()

    def initialize(self):
        super().initialize()
        self.m_PlotShapes=[]    #type:List[int]
        self.m_PlotSizes=[]     #type:List[object]
        self.m_Classifier=None  #type:Classifier
        self.m_ClassIndex=-1
        self.m_Evaluation=None      #type:Evaluation
        self.m_SaveForVisualization=True
        self.m_MinimumPlotSizeNumeric=30
        self.m_MaximumPlotSizeNumeric=200


    def setClassifier(self,value:Classifier):
        self.m_Classifier=value

    def setClassIndex(self,index:int):
        self.m_ClassIndex=index

    def setPointSizeProportionalToMargin(self,b:bool):
        self.m_pointSizeProportionalToMargin=b

    def setEvaluation(self,value:Evaluation):
        self.m_Evaluation=value

    def determineFormat(self):
        margin=None     #type:Attribute
        if not self.m_SaveForVisualization:
            self.m_PlotInstances=None
            return
        hv=[]   #type:List[Attribute]
        classAt=self.m_Instances.attribute(self.m_ClassIndex)
        if classAt.isNominal():
            attVals=[]
            for i in range(classAt.numValues()):
                attVals.append(classAt.value(i))
            predictedClass=Attribute("predicted " + classAt.name(), attVals)
            margin=Attribute("prediction margin")
        else:
            predictedClass=Attribute("predicted" + classAt.name())
        for i in range(self.m_Instances.numAttributes()):
            if i == self.m_Instances.classIndex():
                if classAt.isNominal():
                    hv.append(margin)
                hv.append(predictedClass)
            hv.append(self.m_Instances.attribute(i).copy())
        #添加预测属性
        self.m_PlotInstances=Instances(self.m_Instances.relationName()+"_predicted",hv,self.m_Instances.numInstances())
        if classAt.isNominal():
            self.m_PlotInstances.setClassIndex(self.m_ClassIndex+2)
        else:
            self.m_PlotInstances.setClassIndex(self.m_ClassIndex+1)

    def process(self,toPredict:Instance,classifier:Classifier,evaluation:Evaluation):
        probActual=probNext=pred=0
        classMissing=copy.deepcopy(toPredict)
        classMissing.setDataset(toPredict.dataset())

        if toPredict.classAttribute().isNominal():
            #返回分类预测的概率分布
            preds=classifier.distributionForInstance(classMissing)
            #若概率全部为0，则表示不属于任何一类
            if sum(preds) == 0:
                pred=Utils.missingValue()
                probActual=Utils.missingValue()
            else:
                #分类结果为概率最大的一项下标
                pred=Utils.maxIndex(preds)
                if not Utils.isMissingValue(toPredict.classIndex()):
                    #如果值不缺失，表示非预测样本，不做修改
                    probActual=preds[int(toPredict.classValue())]
                else:
                    probActual=preds[Utils.maxIndex(preds)]
            for i in range(toPredict.classAttribute().numValues()):
                if i != int(toPredict.classValue()) and preds[i] > probNext:
                    probNext=preds[i]
            evaluation.evaluationForSingleInstance(preds,toPredict,True)
        else:
            #单项评估
            pred=evaluation.evaluateModelOnceAndRecordPrediction(classifier,toPredict)
        if not self.m_SaveForVisualization:
            return
        #保存可视化数据
        if self.m_PlotInstances is not None:
            isNominal=toPredict.classAttribute().isNominal()
            values=[0]*self.m_PlotInstances.numAttributes()
            for i in range(self.m_PlotInstances.numAttributes()):
                if i<toPredict.classIndex():
                    values[i]=toPredict.value(i)
                elif i == toPredict.classIndex():
                    if isNominal:
                        #首选结果与备选结果的差值
                        values[i]=probActual-probNext
                        #预测结果
                        values[i+1]=pred
                        #原始值
                        values[i+2]=toPredict.value(i)
                        i+=2
                    else:
                        values[i]=pred
                        values[i+1]=toPredict.value(i)
                        i+=1
                else:
                    if isNominal:
                        values[i]=toPredict.value(i-2)
                    else:
                        values[i]=toPredict.value(i-1)
            # print("============")
            # for m in values:
            #     print("val:",m)
            # print("============")
            self.m_PlotInstances.add(Instance(1.0,values))
            if toPredict.classAttribute().isNominal():
                if toPredict.isMissing(toPredict.classIndex()) or Utils.isMissingValue(pred):
                    self.m_PlotShapes.append(Plot2D.MISSING_SHAPE)
                elif pred != toPredict.classValue():
                    self.m_PlotShapes.append(Plot2D.ERROR_SHAPE)
                else:
                    self.m_PlotShapes.append(Plot2D.CONST_AUTOMATIC_SHAPE)
                if self.m_pointSizeProportionalToMargin:
                    self.m_PlotSizes.append(probActual-probNext)
                else:
                    sizeAdj=0
                    if pred != toPredict.classValue():
                        sizeAdj=1
                    self.m_PlotSizes.append(Plot2D.DEFAULT_SHAPE_SIZE.value+sizeAdj)
            else:
                errd=None
                if not toPredict.isMissing(toPredict.classIndex()) and not Utils.isMissingValue(pred):
                    errd=pred-toPredict.classValue()
                    self.m_PlotShapes.append(Plot2D.CONST_AUTOMATIC_SHAPE)
                else:
                    self.m_PlotShapes.append(Plot2D.MISSING_SHAPE)
                self.m_PlotSizes.append(errd)

    def createPlotData(self,name:str):
        if not self.m_SaveForVisualization:
            return None
        result=PlotData2D(self.m_PlotInstances)
        result.setShapeSize(self.m_PlotSizes)
        result.setShapeType(self.m_PlotShapes)
        result.setPlotName(name+" ("+self.m_Instances.relationName()+")")
        return result

    def finishUp(self):
        super().finishUp()
        if not self.m_SaveForVisualization:
            return
        if self.m_Instances.classAttribute().isNumeric() or self.m_pointSizeProportionalToMargin:
            self.scaleNumericPredictions()

    def scaleNumericPredictions(self):
        maxErr=float("-inf")
        minErr=float("inf")
        if self.m_Instances.classAttribute().isNominal():
            maxErr=1
            minErr=0
        else:
            for i in range(len(self.m_PlotSizes)):
                errd=self.m_PlotSizes[i]
                if errd is not None:
                    err=abs(errd)
                    if err < minErr:
                        minErr=err
                    if err > maxErr:
                        maxErr=err
        for i in range(len(self.m_PlotSizes)):
            errd=self.m_PlotSizes[i]
            if errd is not None:
                err=abs(errd)
                if maxErr - minErr > 0:
                    temp=((err-minErr)/(maxErr-minErr))*(self.m_MaximumPlotSizeNumeric-self.m_MinimumPlotSizeNumeric+1)
                    self.m_PlotSizes[i]=int(temp)+self.m_MinimumPlotSizeNumeric
                else:
                    self.m_PlotSizes[i]=self.m_MinimumPlotSizeNumeric
            else:
                self.m_PlotSizes[i]=self.m_MinimumPlotSizeNumeric

    def cleanUp(self):
        super().cleanUp()
        self.m_Classifier=None
        self.m_PlotShapes=None
        self.m_PlotSizes=None
        self.m_Evaluation=None