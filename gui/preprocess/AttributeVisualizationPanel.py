import copy
import math
from typing import *

import numpy as np
from Attributes import Attribute
from Instances import Instances
from PyQt5.QtCore import *
from SparseInstance import SparseInstance
from Utils import Utils
from MatplotlibWidget import MatplotlibWidget

from core.AttributeStats import AttributeStats
from gui.designUI.Main import Ui_MainWindow


class AttributeVisualizationPanel():
    mutex=QMutex()
    m_colorNames=[ "blue", "red", "cyan","grey_blue", "pink", "green", "orange", "light_pink","red","light_green"]
    def __init__(self,ui:Ui_MainWindow):
        self.m_colorAttribute=ui.attr_combo
        self.m_Painter=ui.draw_area     #type:MatplotlibWidget
        self.m_threadRun=False
        self.m_doneCurrentAttribute=False
        self.m_displayCurrentAttribute=False
        self.m_barRange=0
        self.m_histBarCounts=None       #type:List[float]
        self.m_histBarClassCounts=None  #type:List[SparseInstance]
        self.m_maxValue=None        #type:int
        self.m_colorList=[]       #type:List
        self.m_hc=None          #type:QThread
        self.m_colorAttribute.currentIndexChanged.connect(self.itemChanged)

    def setInstance(self,inst:Instances):
        self.m_attrIndex=0
        self.m_as=None      #type:AttributeStats
        self.m_data=copy.deepcopy(inst)

        self.m_colorAttribute.clear()
        self.m_colorAttribute.addItem("No class")
        for i in range(self.m_data.numAttributes()):
            type="("+Attribute.typeToStringShort(self.m_data.attribute(i).type())+")"
            name=self.m_data.attribute(i).name()
            self.m_colorAttribute.addItem("Class: "+name+" "+type)
        self.m_classIndex=self.m_data.numAttributes()-1
        self.m_colorAttribute.setCurrentIndex(self.m_data.numAttributes())
        self.m_asCache=[None]*self.m_data.numAttributes()       #type:List[AttributeStats]

    def itemChanged(self,index:int):
        self.m_classIndex=self.m_colorAttribute.currentIndex()-1
        if self.m_as is not None:
            self.setAttribute(self.m_attrIndex)

    def setAttribute(self,index:int):
        self.mutex.lock()
        self.m_threadRun=False
        self.m_doneCurrentAttribute=False
        self.m_displayCurrentAttribute=True
        self.m_attrIndex=index
        if self.m_asCache[index] is None:
            self.m_asCache[index]=self.m_data.attributeStats(index)
        self.m_as=self.m_asCache[index]
        self.mutex.unlock()
        self.paint()

    def calcGraph(self,panelWidth:int,panelHeight:int):
        self.mutex.lock()
        self.m_threadRun=True
        if self.m_as.nominalWeights is not None:
            self.m_hc=BarCalc(panelWidth,panelHeight,self)
            self.m_hc.setPriority(QThread.LowestPriority)
            self.m_hc.start()
        elif self.m_as.numericStats is not None:
            self.m_hc=HistCalc(self)
            self.m_hc.setPriority(QThread.LowestPriority)
            self.m_hc.start()
        else:
            self.m_histBarCounts=None
            self.m_histBarClassCounts=None
            self.m_doneCurrentAttribute=True
            self.m_threadRun=False
            self.paint()
        self.mutex.unlock()

    #TODO ToolTipText
    def paint(self):
        self.m_Painter.clear()
        if self.m_as is not None:
            if not self.m_doneCurrentAttribute and not self.m_threadRun:
                self.calcGraph(self.m_Painter.width(),self.m_Painter.height())
            if not self.m_threadRun and self.m_displayCurrentAttribute:
                if self.m_as.nominalWeights is not None and (self.m_histBarClassCounts is not None or self.m_histBarCounts is not None):
                    if self.m_classIndex>=0 and self.m_data.attribute(self.m_classIndex).isNominal():
                        intervalWidth = self.m_Painter.width() / len(self.m_histBarClassCounts)
                        if intervalWidth > 5:
                            barWidth = math.floor(intervalWidth * 0.8)
                        else:
                            barWidth = 1
                        #计算y轴最大值
                        dataList=None
                        first=True
                        nullBarCount=[]
                        for i in range(len(self.m_histBarClassCounts)):
                            if self.m_histBarClassCounts[i] is not None:
                                if first:
                                    dataList=[[] for i in range(self.m_histBarClassCounts[i].numAttributes())]
                                    first=False
                                for j in range(self.m_histBarClassCounts[i].numAttributes()):
                                    dataList[j].append(self.m_histBarClassCounts[i].value(j))
                            else:
                                nullBarCount.append(i)
                        for i in range(len(nullBarCount)):
                            for j in range(len(dataList)):
                                dataList[j].insert(nullBarCount[i],0)
                        dataList=np.array(dataList)

                        self.m_Painter.mpl.paintRect(dataList,barWidth,colorList=self.m_colorList)
                    else:
                        intervalWidth = self.m_Painter.width() / len(self.m_histBarCounts)
                        if intervalWidth > 5:
                            barWidth = math.floor(intervalWidth * 0.8)
                        else:
                            barWidth = 1
                        dataList=np.array([self.m_histBarCounts])
                        self.m_Painter.mpl.paintRect(dataList,barWidth)
                elif self.m_as.numericStats is not None and (self.m_histBarCounts is not None or self.m_histBarClassCounts is not None):
                    if self.m_classIndex>=0 and self.m_data.attribute(self.m_classIndex).isNominal():
                        if (self.m_Painter.width()-6)/len(self.m_histBarClassCounts)<1:
                            barWidth=1
                        else:
                            barWidth=(self.m_Painter.width()-6)/len(self.m_histBarClassCounts)
                        dataList = None
                        newColor=[]
                        first = True
                        nullBarCount=[]
                        for i in range(len(self.m_histBarClassCounts)):
                            if self.m_histBarClassCounts[i] is not None:
                                if first:
                                    dataList=[[] for i in range(self.m_histBarClassCounts[i].numValues())]
                                for j in range(self.m_histBarClassCounts[i].numValues()):
                                    Utils.debugOut("histBarClassCount[",j,"]:",self.m_histBarClassCounts[i].valueSparse(j))
                                    dataList[j].append(self.m_histBarClassCounts[i].valueSparse(j))
                                    if first:
                                        newColor.append(self.m_colorList[self.m_histBarClassCounts[i].positionIndex(j)])
                                first=False
                            else:
                                nullBarCount.append(i)
                        for i in range(len(nullBarCount)):
                            for j in range(len(dataList)):
                                dataList[j].insert(nullBarCount[i],0)
                        dataList=np.array(dataList)
                        Utils.debugOut("AttrVisual_paint_dataList:",dataList)
                        Utils.debugOut("AttrVisual_paint_barWidth:",barWidth)
                        self.m_Painter.mpl.paintRect(dataList,barWidth,isNumeric=True,colorList=newColor)
                    else:
                        if (self.m_Painter.width()-6)/len(self.m_histBarCounts)<1:
                            barWidth=1
                        else:
                            barWidth=(self.m_Painter.width()-6)/len(self.m_histBarCounts)
                        dataList=np.array([self.m_histBarCounts])
                        self.m_Painter.mpl.paintRect(dataList,barWidth,isNumeric=True)
                    self.m_Painter.setXLimt(self.m_as.numericStats.min, self.m_as.numericStats.max,len(dataList[0]))
                else:
                    self.m_Painter.clear()

    def getColoringIndex(self):
        return self.m_classIndex



class BarCalc(QThread):
    def __init__(self,width,height,panel:AttributeVisualizationPanel):
        super().__init__()
        self.m_panel=panel
        self.m_panelWidth=width

    def run(self):
        self.m_panel.mutex.lock()
        if self.m_panel.m_data.attribute(self.m_panel.m_attrIndex).numValues()>self.m_panelWidth:
            self.m_panel.m_histBarClassCounts=None
            self.m_panel.m_threadRun=False
            self.m_panel.m_doneCurrentAttribute=False
            self.m_panel.m_displayCurrentAttribute=False
            # self.m_panel.paint()
            return

        if self.m_panel.m_classIndex>=0 and self.m_panel.m_data.attribute(self.m_panel.m_classIndex).isNominal():
            histClassCount=[None]*self.m_panel.m_data.attribute(self.m_panel.m_attrIndex).numValues()

            if len(self.m_panel.m_as.nominalWeights)>0:
                self.m_panel.m_maxValue=self.m_panel.m_as.nominalWeights[0]
                for i in range(self.m_panel.m_data.attribute(self.m_panel.m_attrIndex).numValues()):
                    if self.m_panel.m_as.nominalWeights[i]>self.m_panel.m_maxValue:
                        self.m_panel.m_maxValue=self.m_panel.m_as.nominalWeights[i]
            else:
                self.m_panel.m_maxValue=0

            if len(self.m_panel.m_colorList) == 0:
                self.m_panel.m_colorList.append("black")

            for i in range(len(self.m_panel.m_colorList),self.m_panel.m_data.attribute(self.m_panel.m_classIndex).
                    numValues()+1):
                colorStr=AttributeVisualizationPanel.m_colorNames[(i - 1) % 10]
                self.m_panel.m_colorList.append(colorStr)

            self.m_panel.m_data.sort(self.m_panel.m_attrIndex)
            tempClassCounts=None    #type:List[float]
            tempAttValueIndex=-1

            for k in range(self.m_panel.m_data.numInstances()):
                if not self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_attrIndex):
                    if self.m_panel.m_data.instance(k).value(self.m_panel.m_attrIndex) != tempAttValueIndex:
                        if tempClassCounts is not None:
                            numNonZero=0
                            for tempClassCount in tempClassCounts:
                                if tempClassCount>0:
                                    numNonZero+=1
                            nonZeroVals=[0.0]*numNonZero
                            nonZeroIndics=[0]*numNonZero
                            count=0
                            for z in range(len(tempClassCounts)):
                                if tempClassCounts[z]>0:
                                    nonZeroVals[count]=tempClassCounts[z]
                                    nonZeroIndics[count]=z
                                    count+=1

                            tempSparse=SparseInstance(1.0,nonZeroVals,nonZeroIndics,len(tempClassCounts))
                            histClassCount[tempAttValueIndex]=tempSparse

                        #0下标存储缺失数据
                        tempClassCounts=[0.0]*(self.m_panel.m_data.attribute(self.m_panel.m_classIndex).numValues()+1)
                        tempAttValueIndex=int(self.m_panel.m_data.instance(k).value(self.m_panel.m_attrIndex))

                    if self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_classIndex):
                        tempClassCounts[0]+=self.m_panel.m_data.instance(k).weight()
                    else:
                        tempClassCounts[(int)(self.m_panel.m_data.instance(k).value(self.m_panel.m_classIndex)+1)]+=self.m_panel.m_data.instance(k).weight()

            if tempClassCounts is not None:
                numNonZero=0
                for tempClassCount in tempClassCounts:
                    if tempClassCount>0:
                        numNonZero+=1
                nonZeroVals=[0.0]*numNonZero
                nonZeroIndics=[0]*numNonZero
                count=0
                for z in range(len(tempClassCounts)):
                    if tempClassCounts[z]>0:
                        nonZeroVals[count]=tempClassCounts[z]
                        nonZeroIndics[count]=z
                        count+=1

                tempSparse=SparseInstance(1.0,nonZeroVals,nonZeroIndics,len(tempClassCounts))
                histClassCount[tempAttValueIndex]=tempSparse

            self.m_panel.m_threadRun=False
            self.m_panel.m_doneCurrentAttribute=True
            self.m_panel.m_displayCurrentAttribute=True
            self.m_panel.m_histBarClassCounts=histClassCount
            self.m_panel.paint()
        else:
            histCounts=[0.0]*self.m_panel.m_data.attribute(self.m_panel.m_attrIndex).numValues()     #type:List[float]
            if len(self.m_panel.m_as.nominalWeights)>0:
                self.m_panel.m_maxValue=self.m_panel.m_as.nominalWeights[0]
                for i in range(self.m_panel.m_data.attribute(self.m_panel.m_attrIndex).numValues()):
                    if self.m_panel.m_as.nominalWeights[i]>self.m_panel.m_maxValue:
                        self.m_panel.m_maxValue=self.m_panel.m_as.nominalWeights[i]
            else:
                self.m_panel.m_maxValue=0

            for k in range(self.m_panel.m_data.numInstances()):
                if not self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_attrIndex):
                    histCounts[int(self.m_panel.m_data.instance(k).value(self.m_panel.m_attrIndex))]+=self.m_panel.m_data.instance(k).weight()

            self.m_panel.m_threadRun=False
            self.m_panel.m_doneCurrentAttribute=True
            self.m_panel.m_displayCurrentAttribute=True
            self.m_panel.m_histBarCounts=histCounts
            self.m_panel.paint()

        self.m_panel.mutex.unlock()

class HistCalc(QThread):
    def __init__(self,panel:AttributeVisualizationPanel):
        super().__init__()
        self.m_panel=panel

    def run(self):
        self.m_panel.mutex.lock()

        if self.m_panel.m_classIndex>=0 and self.m_panel.m_data.attribute(self.m_panel.m_classIndex).isNominal():
            intervalWidth=3.49*self.m_panel.m_as.numericStats.stdDev*math.pow(self.m_panel.m_data.numInstances(),-1/3)
            intervals=max(1,int(round((self.m_panel.m_as.numericStats.max-self.m_panel.m_as.numericStats.min)/intervalWidth)))

            # print(self.m_panel.m_Painter.width())
            if intervals > self.m_panel.m_Painter.width():
                #像素填充
                intervals=self.m_panel.m_Painter.width()-6
                if intervals<1:
                    intervals=1
            histClassCounts=[[0]*(self.m_panel.m_data.attribute(self.m_panel.m_classIndex).numValues()+1) for i in range(intervals)]
            Utils.debugOut("max",self.m_panel.m_as.numericStats.max)
            Utils.debugOut("min",self.m_panel.m_as.numericStats.min)
            Utils.debugOut("intervalWidth",intervalWidth)
            Utils.debugOut("len",len(histClassCounts))
            Utils.debugOut("histClasCount:",histClassCounts)
            barRange=(self.m_panel.m_as.numericStats.max-self.m_panel.m_as.numericStats.min)/len(histClassCounts)

            self.m_panel.m_maxValue=0
            if len(self.m_panel.m_colorList)==0:
                self.m_panel.m_colorList.append("black")

            for i in range(len(self.m_panel.m_colorList),self.m_panel.m_data.attribute(self.m_panel.m_classIndex).
                    numValues()+1):
                colorStr=AttributeVisualizationPanel.m_colorNames[(i - 1) % 10]
                self.m_panel.m_colorList.append(colorStr)

            for k in range(self.m_panel.m_data.numInstances()):
                if not self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_attrIndex):
                    t=int(math.ceil((self.m_panel.m_data.instance(k).value(self.m_panel.m_attrIndex)-self.m_panel.m_as.numericStats.min)/barRange))
                    if t==0:
                        if self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_classIndex):
                            histClassCounts[t][0]+=self.m_panel.m_data.instance(k).weight()
                        else:
                            histClassCounts[t][int(self.m_panel.m_data.instance(k).value(self.m_panel.m_classIndex)+1)]+=self.m_panel.m_data.instance(k).weight()
                    else:
                        if self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_classIndex):
                            histClassCounts[t-1][0]+=self.m_panel.m_data.instance(k).weight()
                        else:
                            histClassCounts[t-1][int(self.m_panel.m_data.instance(k).value(self.m_panel.m_classIndex)+1)]+=self.m_panel.m_data.instance(k).weight()



            for histClassCount in histClassCounts:
                sum=0
                for element in histClassCount:
                    sum+=element
                if self.m_panel.m_maxValue<sum:
                    self.m_panel.m_maxValue=sum

            histClassCountsSparse=[None]*len(histClassCounts)
            for i in range(len(histClassCounts)):
                numSparseValues=0
                for j in range(len(histClassCounts[i])):
                    if histClassCounts[i][j]>0:
                        numSparseValues+=1
                sparseValues=[0]*numSparseValues
                sparseIndices=[0]*numSparseValues
                count=0
                for j in range(len(histClassCounts[i])):
                    if histClassCounts[i][j]>0:
                        sparseValues[count]=histClassCounts[i][j]
                        sparseIndices[count]=j
                        count+=1
                tempSparse=SparseInstance(1.0,sparseValues,sparseIndices,len(histClassCounts[i]))
                histClassCountsSparse[i]=tempSparse

            self.m_panel.m_histBarClassCounts=histClassCountsSparse
            self.m_panel.m_barRange=barRange
        else:
            intervalWidth=3.49*self.m_panel.m_as.numericStats.stdDev*math.pow(self.m_panel.m_data.numInstances(),-1/3)
            intervals=max(1,round((self.m_panel.m_as.numericStats.max-self.m_panel.m_as.numericStats.min)/intervalWidth))
            if intervals > self.m_panel.m_Painter.width():
                intervals=self.m_panel.m_Painter.width()-6
                if intervals<1:
                    intervals=1
            histCounts=[0]*intervals
            barRange=(self.m_panel.m_as.numericStats.max-self.m_panel.m_as.numericStats.min)/len(histCounts)
            self.m_panel.m_maxValue=0

            for k in range(self.m_panel.m_data.numInstances()):
                if self.m_panel.m_data.instance(k).isMissing(self.m_panel.m_attrIndex):
                    continue
                t=int(math.ceil((self.m_panel.m_data.instance(k).value(self.m_panel.m_attrIndex)-self.m_panel.m_as.numericStats.min)/barRange))
                if t==0:
                    histCounts[t]+=self.m_panel.m_data.instance(k).weight()
                    if histCounts[t]>self.m_panel.m_maxValue:
                        self.m_panel.m_maxValue=histCounts[t]
                else:
                    histCounts[t-1]+=self.m_panel.m_data.instance(k).weight()
                    if histCounts[t-1]>self.m_panel.m_maxValue:
                        self.m_panel.m_maxValue=histCounts[t-1]
            self.m_panel.m_histBarCounts=histCounts
            self.m_panel.m_barRange=barRange
        self.m_panel.m_threadRun=False
        self.m_panel.m_displayCurrentAttribute=True
        self.m_panel.m_doneCurrentAttribute=True
        self.m_panel.paint()

        self.m_panel.mutex.unlock()



