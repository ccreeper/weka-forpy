from typing import *
from AbstractPlotInstances import AbstractPlotInstances
from classifiers.Evaluation import Evaluation
from Instances import Instances,Instance
from Attributes import Attribute
from classifiers.Classifier import Classifier

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
        self.m_MinimumPlotSizeNumeric=1
        self.m_MaximumPlotSizeNumeric=20

    def setInstances(self,value:Instances):
        self.m_Instances=value

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
        self.m_PlotInstances=Instances(self.m_Instances.relationName()+"_predicted",hv,self.m_Instances.numInstances())
        if classAt.isNominal():
            self.m_PlotInstances.setClassIndex(self.m_ClassIndex+2)
        else:
            self.m_PlotInstances.setClassIndex(self.m_ClassIndex+1)

    def process(self,toPredict:Instance,classifier:Classifier,evaluation:Evaluation):

        #TODO