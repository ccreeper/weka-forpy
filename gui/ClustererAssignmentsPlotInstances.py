from typing import *

from gui.AbstractPlotInstances import AbstractPlotInstances
from core.Attributes import Attribute
from core.Instances import Instances, Instance

from clusterers.ClusterEvaluation import ClusterEvaluation
from clusterers.Clusterer import Clusterer
from core.Utils import Utils
from gui.PlotData2D import PlotData2D
from gui.classifier.Plot2D import Plot2D


class ClustererAssignmentsPlotInstances(AbstractPlotInstances):
    def initialize(self):
        super().initialize()
        self.m_PlotShapes=None  #type:List[int]
        self.m_Clusterer=None   #type:Clusterer
        self.m_Evaluation=None  #type:ClusterEvaluation

    def setClusterer(self,value:Clusterer):
        self.m_Clusterer=value

    def setClusterEvaluation(self,value:ClusterEvaluation):
        self.m_Evaluation=value

    def finishUp(self):
        super().finishUp()
        self.process()

    def determineFormat(self):
        numClusters=self.m_Evaluation.getNumClusters()
        hv=[]
        clustVals=[]
        for i in range(numClusters):
            clustVals.append("cluster"+str(i))
        predictedCluster=Attribute("Cluster",clustVals)
        for i in range(self.m_Instances.numAttributes()):
            hv.append(self.m_Instances.attribute(i).copy())
        hv.append(predictedCluster)
        self.m_PlotInstances=Instances(self.m_Instances.relationName()+"_clustered",hv,self.m_Instances.numInstances())

    def process(self):
        clusterAssignments=self.m_Evaluation.getClusterAssignments()
        classAssignments=None
        j=0
        if self.m_Instances.classIndex() >= 0:
            classAssignments=self.m_Evaluation.getClassesToClusters()
            self.m_PlotShapes=[]
            for i in range(self.m_Instances.numInstances()):
                self.m_PlotShapes.append(Plot2D.CONST_AUTOMATIC_SHAPE)
        for i in clusterAssignments:
            print(",",i,end="")
        print()
        for i in range(self.m_Instances.numInstances()):
            values=[0]*self.m_PlotInstances.numAttributes()
            for j in range(self.m_Instances.numAttributes()):
                values[j]=self.m_Instances.instance(i).value(j)
            if clusterAssignments[i] < 0:
                values[j+1]= Utils.missingValue()
            else:
                values[j+1]=clusterAssignments[i]
            self.m_PlotInstances.add(Instance(1.0,values))
            if self.m_PlotShapes is not None:
                if clusterAssignments[i] >= 0:
                    if int(self.m_Instances.instance(i).classValue()) != classAssignments[int(clusterAssignments[i])]:
                        self.m_PlotShapes[i]=Plot2D.ERROR_SHAPE
                else:
                    self.m_PlotShapes[i]=Plot2D.MISSING_SHAPE


    def createPlotData(self,name:str):
        result=PlotData2D(self.m_PlotInstances)
        if self.m_PlotShapes is not None:
            result.setShapeType(self.m_PlotShapes)
        result.addInstanceNumberAttribute()
        result.setPlotName(name+" ("+self.m_Instances.relationName()+")")
        return result

    def cleanUp(self):
        super(ClustererAssignmentsPlotInstances, self).cleanUp()
        self.m_Clusterer=None
        self.m_Evaluation=None      #type:ClusterEvaluation
        self.m_PlotShapes=None