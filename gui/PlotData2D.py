from typing import *
from Instances import Instances,Instance
from gui.classifier.Plot2D import Plot2D
from filters.attribute.Add import Add
from filters.Filter import Filter
import math

class PlotData2D():
    def __init__(self,insts:Instances):
        self.m_maxX=self.m_minX=self.m_maxY=self.m_minY=self.m_maxC=self.m_minC=0
        self.m_plotName="new plot"
        self.m_plotInstances=insts
        self.m_xIndex=self.m_yIndex=self.m_cIndex=0
        self.m_pointLookup=[[0]*4 for i in range(insts.numInstances())]
        self.m_shapeSize=[]           #type:List[int]
        self.m_shapeType=[]           #type:List[int]
        self.m_connecctPoints=[False]*insts.numInstances()
        self.m_alwaysDisplayPointsOfThisSize=-1
        self.m_displayAllPoints=False
        for i in range(insts.numInstances()):
            self.m_shapeSize.append(Plot2D.DEFAULT_SHAPE_SIZE)
            if self.m_plotInstances.instance(i).weight() >= 0:
                self.m_shapeType.append(Plot2D.CONST_AUTOMATIC_SHAPE)
            else:
                self.m_shapeType.append(-2)
        self.determineBounds()

    def determineBounds(self):
        if self.m_plotInstances is not None and self.m_plotInstances.numAttributes()>0 and self.m_plotInstances.numInstances()>0:
            min=float('inf')
            max=float('-inf')
            if self.m_plotInstances.attribute(self.m_xIndex).isNominal():
                self.m_minX=0
                self.m_maxX=self.m_plotInstances.attribute(self.m_xIndex).numValues()-1
            else:
                for i in range(self.m_plotInstances.numInstances()):
                    if not self.m_plotInstances.instance(i).isMissing(self.m_xIndex):
                        value=self.m_plotInstances.instance(i).value(self.m_xIndex)
                        if value < min:
                            min=value
                        if value > max:
                            max=value
                if min == float("inf"):
                    min=max=0
                self.m_minX=min
                self.m_maxX=max
                if min == max:
                    self.m_maxX+=0.05
                    self.m_minX-=0.05
            min=float('inf')
            max=float('-inf')
            if self.m_plotInstances.attribute(self.m_yIndex).isNominal():
                self.m_minY=0
                self.m_maxY=self.m_plotInstances.attribute(self.m_yIndex).numValues()-1
            else:
                for i in range(self.m_plotInstances.numInstances()):
                    if not self.m_plotInstances.instance(i).isMissing(self.m_yIndex):
                        value=self.m_plotInstances.instance(i).value(self.m_yIndex)
                        if value < min:
                            min=value
                        if value > max:
                            max=value
                if min == float('inf'):
                    min=max=0
                self.m_minY=min
                self.m_maxY=max
                if min == max:
                    self.m_maxY+=0.05
                    self.m_minY-=0.05
            min=float("inf")
            max=float("-inf")
            for i in range(self.m_plotInstances.numInstances()):
                if not self.m_plotInstances.instance(i).isMissing(self.m_cIndex):
                    value=self.m_plotInstances.instance(i).value(self.m_cIndex)
                    if value < min:
                        min=value
                    if value > max:
                        max=value
            if min == float('inf'):
                min=max=0
            self.m_minC=min
            self.m_maxC=max

    def setShapeSize(self,ss:List):
        if len(ss) != self.m_plotInstances.numInstances():
            raise Exception("PlotData2D: Shape size vector must have the same "
                            + "number of entries as number of data points!")
        self.m_shapeSize=[]
        for i in range(len(ss)):
            self.m_shapeSize.append(ss[i])

    def setShapeType(self,st:List):
        if len(st) != self.m_plotInstances.numInstances():
            raise Exception("PlotData2D: Shape size vector must have the same "
                            + "number of entries as number of data points!")
        self.m_shapeType=[]
        for i in range(len(st)):
            self.m_shapeType.append(st[i])

    def addInstanceNumberAttribute(self):
        originalRelationName=self.m_plotInstances.relationName()
        originalClassIndex=self.m_plotInstances.classIndex()
        addF=Add()
        addF.setAttributeName("Instance_number")
        addF.setAttributeIndex("first")
        addF.setInputFormat(self.m_plotInstances)
        self.m_plotInstances=Filter.useFilter(self.m_plotInstances,addF)
        self.m_plotInstances.setClassIndex(originalClassIndex+1)
        for i in range(self.m_plotInstances.numInstances()):
            self.m_plotInstances.instance(i).setValue(0,i)
        self.m_plotInstances.setRelationName(originalRelationName)


    def setXindex(self,x:int):
        self.m_xIndex=x
        self.determineBounds()

    def setYindex(self,y:int):
        self.m_yIndex=y
        self.determineBounds()

    def setCindex(self,c:int):
        self.m_cIndex=c
        self.determineBounds()

    def setPlotName(self,name:str):
        self.m_plotName=name
