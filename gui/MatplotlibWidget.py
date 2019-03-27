import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
import numpy as np
from typing import *
from core.Utils import Utils
from PlotData2D import PlotData2D
from gui.classifier.Plot2D import Plot2D
from Instances import Instances,Instance
import ast
import math

class MyMplCanvas(FigureCanvas):
    m_defaultColors = {
        "white": "#FFFFFF",
        "black": "#000000",
        "blue": "#0000FF",
        "red": "#FF0000",
        "cyan": "#00FFFF",
        "grey_blue": "#4B7B82",
        "pink": "#FFAFAF",
        "green": "#00FF00",
        "orange": "#FFC800",
        "light_pink": "#FF00FF"}
    m_defaultColorsName=["blue","red","cyan","grey_blue","pink","green","orange","light_pink","red","grenn","white"]
    m_markers={
        Plot2D.MISSING_SHAPE.value:"1",
        Plot2D.ERROR_SHAPE.value:"s",
        Plot2D.DIAMOND_SHAPE.value:"D",
        Plot2D.X_SHAPE.value:"x",
        Plot2D.PLUS_SHAPE.value:"+",
        Plot2D.TRIANGLEDOWN_SHAPE.value:"v",
        Plot2D.TRIANGLEUP_SHAPE.value:"^"
    }
    def __init__(self,parent=None,width=5,height=4,dpi=100):
        #显示中文
        plt.rcParams['font.family']=['SimHei']
        #字体大小
        # plt.rcParams['font.size']=10
        #显示负号
        plt.rcParams['axes.unicode_minus']=False
        # plt.style.use("dark_background")

        self.fig=Figure(figsize=(width,height),dpi=dpi)

        self.axes=self.fig.add_subplot(111)

        self.axes.set_xticks([])
        self.axes.set_yticks([])
        #去留白
        self.fig.subplots_adjust(top=1, bottom=0.1, left=0, right=1, hspace=0, wspace=0)

        #去边框
        self.showFrame(False)

        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.initData()


    def initData(self):
        self.m_drawnPoints=[]
        self.m_colorList=[]
        self.m_plots=[]     #type:List[PlotData2D]
        self.m_masterPlot=None      #type:PlotData2D
        self.m_plotInstances=None       #type:Instances
        self.m_xIndex = self.m_yIndex = self.m_cIndex =  self.m_sIndex = 0
        self.m_maxX=self.m_minX=self.m_maxY=self.m_minY=self.m_maxC=self.m_minC=0
        self.m_XaxisEnd=self.m_YaxisEnd=self.m_XaxisStart=self.m_YaxisStart=0
        self.m_axisChanged=False
        self.m_plotResize=True
        for i in range(10):
            pc=self.m_defaultColors.get(self.m_defaultColorsName[i%10])
            self.m_colorList.append(pc)

    def getPlots(self)->List[PlotData2D]:
        return self.m_plots

    def addPlot(self,newPlot:PlotData2D):
        if newPlot.m_plotInstances is None:
            raise Exception("No instances in plot data!")
        self.m_masterPlot=newPlot
        self.m_plotInstances=self.m_masterPlot.m_plotInstances
        # print("plotInstance numIns:",self.m_plotInstances.numInstances())
        # print("plotInstance attIns:",self.m_plotInstances.numAttributes())
        self.m_plots.append(newPlot)
        self.setXindex(self.m_xIndex)
        self.setYindex(self.m_yIndex)
        self.setCindex(self.m_cIndex)

    def setXindex(self,x:int):
        self.m_xIndex=x
        for i in range(len(self.m_plots)):
            self.m_plots[i].setXindex(self.m_xIndex)
        # print("mplot size:",len(self.m_plots))
        # print("x:",x)
        self.determineBounds()
        self.m_axisChanged=True


    def setYindex(self,y:int):
        self.m_yIndex=y
        for i in range(len(self.m_plots)):
            self.m_plots[i].setYindex(self.m_yIndex)
        self.determineBounds()
        self.m_axisChanged=True

    def setCindex(self,c:int):
        self.m_cIndex=c
        for i in range(len(self.m_plots)):
            self.m_plots[i].setCindex(self.m_cIndex)
        self.determineBounds()
        self.m_axisChanged=True

    def determineBounds(self):
        self.m_minX=self.m_plots[0].m_minX
        self.m_maxX=self.m_plots[0].m_maxX
        self.m_minY=self.m_plots[0].m_minY
        self.m_maxY=self.m_plots[0].m_maxY
        self.m_minC=self.m_plots[0].m_minC
        self.m_maxC=self.m_plots[0].m_maxC
        for i in range(len(self.m_plots)):
            value=self.m_plots[i].m_minX
            if value < self.m_minX:
                self.m_minX=value
            value = self.m_plots[i].m_maxX
            if value > self.m_maxX:
                self.m_maxX=value
            value=self.m_plots[i].m_minY
            if value < self.m_minY:
                self.m_minY=value
            value=self.m_plots[i].m_maxY
            if value > self.m_maxY:
                self.m_maxY=value
            value=self.m_plots[i].m_minC
            if value < self.m_minC:
                self.m_minC=value
            value=self.m_plots[i].m_maxC
            if value > self.m_maxC:
                self.m_maxC=value
        # print("minX:",self.m_minX)
        # print("maxX:",self.m_maxX)
        # print("minY:",self.m_minY)
        # print("maxY:",self.m_maxY)
        # print("minC:",self.m_minC)
        # print("maxC:",self.m_maxC)
        self.fillLookup()

    def fillLookup(self):
        for j in range(len(self.m_plots)):
            temp_plot=self.m_plots[j]
            if temp_plot.m_plotInstances.numInstances() > 0 and temp_plot.m_plotInstances.numAttributes() > 0:
                for i in range(temp_plot.m_plotInstances.numInstances()):
                    if temp_plot.m_plotInstances.instance(i).isMissing(self.m_xIndex) or \
                        temp_plot.m_plotInstances.instance(i).isMissing(self.m_yIndex):
                        temp_plot.m_pointLookup[i][0]=float("-inf")
                        temp_plot.m_pointLookup[i][1]=float("-inf")
                    else:
                        x=temp_plot.m_plotInstances.instance(i).value(self.m_xIndex)
                        y=temp_plot.m_plotInstances.instance(i).value(self.m_yIndex)
                        temp_plot.m_pointLookup[i][0]=x
                        temp_plot.m_pointLookup[i][1]=y
        # print("==================")
        # for plot in self.m_plots:
        #     for i in range(plot.m_plotInstances.numInstances()):
        #         print(i,"_0:",plot.m_pointLookup[i][0])
        #         print(i,"_1:",plot.m_pointLookup[i][1])
        # print("===================")

    def clear(self):
        self.axes.cla()
        self.axes.set_xticks([])
        self.axes.set_yticks([])
    #
    # def convertToPanelX(self,xval:float):
    #     temp=(xval-self.m_minX)/(self.m_maxX-self.m_minX)
    #     temp2=temp*(self.m_XaxisEnd-self.m_XaxisStart)
    #     temp2+=self.m_XaxisStart
    #     return temp2
    #
    # def convertToPanelY(self,yval:float):
    #     temp=(yval-self.m_minY)/(self.m_maxY-self.m_minY)
    #     temp2=temp*(self.m_YaxisEnd-self.m_YaxisStart)
    #     temp2=self.m_YaxisEnd-temp2
    #     return temp2

    def getMasterPlot(self):
        return self.m_masterPlot

    def showFrame(self,flag:bool):
        self.fig.gca().spines['top'].set_visible(flag)
        self.fig.gca().spines['bottom'].set_visible(flag)
        self.fig.gca().spines['left'].set_visible(flag)
        self.fig.gca().spines['right'].set_visible(flag)

    def paintRect(self,dataSet:np.ndarray,barWidth:int,isNumeric:bool=False,colorList:List[str]=("black"),labels:List[str]=None):
        self.showFrame(False)
        self.fig.subplots_adjust(top=0.99, bottom=0.1, left=0.01, right=0.99, hspace=0, wspace=0)
        x = np.arange(len(dataSet[0]))
        # 堆积柱状图
        #width=(max-min)/(x-1)
        Utils.debugOut("colorList:",colorList)
        Utils.debugOut("barWidth:",barWidth)
        sum=[0]*x
        height=[0]*x
        bottom=np.array([0.0]*len(x))
        width=0.8
        maxHeight=0
        a=None
        if isNumeric:
            width=1
        for i in range(len(dataSet)):
            try:
                colorName=colorList[i]
                Utils.debugOut("Matplotlib_paintRect_width:",width)
                Utils.debugOut("Matplotlib_paintRect_colorName:",colorName)
                label=None
                if labels is not None:
                    label=labels[i]
                a=self.axes.bar(x, dataSet[i],bottom=bottom,color=self.m_defaultColors.get(colorName),
                                width=width,label=label)
                bottom+=dataSet[i]
                for j in range(len(dataSet[i])):
                    sum[j]+=dataSet[i][j]
                    maxHeight=max(maxHeight,sum[j])
                    height[j]+=a[j].get_height()
            except IndexError:
                print("dataSet.len:",len(dataSet))
                print("colorList.len:",len(colorList))
                print("colorList:",colorList)

        for i in x:
            self.axes.text(a[i].get_x()+a[i].get_width()/2,height[i],"%d"%int(sum[i]),ha='center',va='bottom')

        self.axes.set_xticks([])
        self.axes.set_yticks([])
        if labels is not None:
            self.axes.legend(loc='upper right')
        if maxHeight != 0:
            self.axes.set_ylim(0,maxHeight*1.1)
        # 显示范围
        #l=min+width*x-(max-min)/2
        #r=max+width*x-(max-min)/2
        # self.axes.set_xlim(11, 69)
        # self.axes.set_ylim(15, 400)
        self.draw()

    def paintPoint(self):
        self.clear()
        # print("xStart: ",self.m_XaxisStart,"xEnd: ",self.m_XaxisEnd)
        # print("yStart: ",self.m_YaxisStart,"yEnd: ",self.m_YaxisEnd)
        self.fig.subplots_adjust(top=0.95, bottom=0.1, left=0.15, right=0.95, hspace=0, wspace=0)
        self.paintAxis()
        #去除上边框右边框
        self.showFrame(True)
        ax=plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if self.m_plotInstances is not None and self.m_plotInstances.numInstances() > 0\
            and self.m_plotInstances.numAttributes() > 0:
            self.paintAxis()
            if self.m_axisChanged or self.m_plotResize:
                x_range=self.m_XaxisEnd-self.m_XaxisStart
                y_range=self.m_YaxisEnd-self.m_YaxisStart
                if x_range < 10:
                    x_range=10
                if y_range < 10:
                    y_range=10
                self.m_drawnPoints=[[0]*(y_range+1) for i in range(x_range+1)]
                self.fillLookup()
                self.m_plotResize=False
                self.m_axisChanged=False
            self.paintData()
        self.draw()



    def paintAxis(self):
        whole =int(abs(self.m_maxX))
        decimal=abs(self.m_maxX)-whole
        if whole > 0:
            nondecimal=int(math.log(whole)/math.log(10))
        else:
            nondecimal=1

        if decimal > 0:
            precisionXmax=int(abs(math.log(abs(self.m_maxX)) / math.log(10))) + 2
        else:
            precisionXmax=1
        if precisionXmax > 10:
            precisionXmax=1
        maxStringX=Utils.doubleToString(self.m_maxX,nondecimal+1+precisionXmax,precisionXmax)

        whole=int(abs(self.m_minX))
        decimal=abs(self.m_minX)-whole
        if whole > 0:
            nondecimal = int(math.log(whole) / math.log(10))
        else:
            nondecimal = 1

        if decimal > 0:
            precisionXmin = int(abs(math.log(abs(self.m_minX)) / math.log(10))) + 2
        else:
            precisionXmin = 1
        if precisionXmin > 10:
            precisionXmin = 1
        minStringX=Utils.doubleToString(self.m_minX,nondecimal+1+precisionXmin,precisionXmin)

        whole = int(abs(self.m_maxY))
        decimal = abs(self.m_maxY) - whole
        if whole > 0:
            nondecimal = int(math.log(whole) / math.log(10))
        else:
            nondecimal = 1

        if decimal > 0:
            precisionYmax = int(abs(math.log(abs(self.m_maxY)) / math.log(10))) + 2
        else:
            precisionYmax = 1
        if precisionYmax > 10:
            precisionYmax = 1
        maxStringY=Utils.doubleToString(self.m_maxY,nondecimal+1+precisionYmax,precisionYmax)

        whole = int(abs(self.m_minY))
        decimal = abs(self.m_minY) - whole
        if whole > 0:
            nondecimal = int(math.log(whole) / math.log(10))
        else:
            nondecimal = 1

        if decimal > 0:
            precisionYmin = int(abs(math.log(abs(self.m_minY)) / math.log(10))) + 2
        else:
            precisionYmin = 1
        if precisionYmin > 10:
            precisionYmin = 1
        minStringY=Utils.doubleToString(self.m_minY,nondecimal+1+precisionYmin,precisionYmin)

        if self.m_plotInstances.attribute(self.m_xIndex).isNumeric():
            mid=(self.m_minX+self.m_maxX)/2
            whole = int(abs(mid))
            decimal = abs(mid) - whole
            if whole > 0:
                nondecimal = int(math.log(whole) / math.log(10))
            else:
                nondecimal = 1

            if decimal > 0:
                precisionXmid = int(abs(math.log(abs(mid)) / math.log(10))) + 2
            else:
                precisionXmid = 1
            if precisionXmid > 10:
                precisionXmid = 1
            maxString=Utils.doubleToString(mid,nondecimal+1+precisionXmid,precisionXmid)

            ticks = [self.m_minX,(self.m_minX+self.m_maxX)/2, self.m_maxX]
            self.axes.set_xticks(ticks)
            labelNumber = [minStringX, maxString, maxStringX]
            self.axes.set_xlim(self.m_minX,self.m_maxX)
            self.axes.set_xticklabels(labelNumber)
        else:
            numValues=self.m_plotInstances.attribute(self.m_xIndex).numValues()
            x = np.arange(0,numValues)
            self.axes.set_xticks(x)
            label=[]
            subFlag=False
            if numValues > 10:
                subFlag=True
            for i in range(numValues):
                if subFlag:
                    label.append(self.m_plotInstances.attribute(self.m_xIndex).value(i)[:3])
                else:
                    label.append(self.m_plotInstances.attribute(self.m_xIndex).value(i))
            self.axes.set_xticklabels(label)
            self.axes.set_xlim(self.m_minX,self.m_maxX)

        if self.m_plotInstances.attribute(self.m_yIndex).isNumeric():
            ticks = [self.m_minY,(self.m_minY+self.m_maxY)/2, self.m_maxY]
            self.axes.set_yticks(ticks)
            mid=(self.m_minY+self.m_maxY)/2
            whole = int(abs(mid))
            decimal = abs(mid) - whole
            if whole > 0:
                nondecimal = int(math.log(whole) / math.log(10))
            else:
                nondecimal = 1

            if decimal > 0:
                precisionYmid = int(abs(math.log(abs(mid)) / math.log(10))) + 2
            else:
                precisionYmid = 1
            if precisionYmid > 10:
                precisionYmid = 1
            maxString = Utils.doubleToString(mid, nondecimal + 1 + precisionYmid, precisionYmid)
            labelNumber = [minStringY,maxString, maxStringY]
            self.axes.set_yticklabels(labelNumber)
            self.axes.set_ylim(self.m_minY,self.m_maxY)
        else:
            numValues = self.m_plotInstances.attribute(self.m_yIndex).numValues()
            x = np.arange(0, numValues)
            self.axes.set_yticks(x)
            label = []
            subFlag = False
            if numValues > 10:
                subFlag = True
            for i in range(numValues):
                if subFlag:
                    label.append(self.m_plotInstances.attribute(self.m_yIndex).value(i)[:3])
                else:
                    label.append(self.m_plotInstances.attribute(self.m_yIndex).value(i))
            self.axes.set_yticklabels(label)
            self.axes.set_ylim(self.m_minY, self.m_maxY)


    def paintData(self):
        for j in range(len(self.m_plots)):
            temp_plot=self.m_plots[j]
            for i in range(temp_plot.m_plotInstances.numInstances()):
                if temp_plot.m_plotInstances.instance(i).isMissing(self.m_xIndex) or \
                    temp_plot.m_plotInstances.instance(i).isMissing(self.m_yIndex):
                    pass
                else:
                    x=temp_plot.m_pointLookup[i][0]+temp_plot.m_pointLookup[i][2]
                    y=temp_plot.m_pointLookup[i][1]+temp_plot.m_pointLookup[i][3]
                    # prevx=prevy=0
                    # if i > 0:
                        #TODO 上点坐标，可用于连线
                        # prevx=temp_plot.m_pointLookup[i-1][0]+temp_plot.m_pointLookup[i-1][2]
                        # prevy=temp_plot.m_pointLookup[i-1][1]+temp_plot.m_pointLookup[i-1][3]
                    # self.m_cIndex=12
                    if temp_plot.m_plotInstances.attribute(self.m_cIndex).isNominal():
                        if temp_plot.m_plotInstances.instance(i).isMissing(self.m_cIndex):
                            color="#708090"
                        else:
                            ind=temp_plot.m_plotInstances.instance(i).value(self.m_cIndex)
                            color=self.m_colorList[ind]
                        if temp_plot.m_plotInstances.instance(i).isMissing(self.m_cIndex):
                            #TODO 连线
                            # if temp_plot.m_connecctPoints[i]:
                            #     pass
                            self.drawDataPoint(x,y,temp_plot.m_shapeSize[i],color,Plot2D.MISSING_SHAPE.value)
                        else:
                            if temp_plot.m_shapeType[i] == Plot2D.CONST_AUTOMATIC_SHAPE:
                                # if temp_plot.m_connecctPoints[i]:
                                self.drawDataPoint(x,y,temp_plot.m_shapeSize[i],color,j)
                            else:
                                # if temp_plot.m_connecctPoints[i]
                                self.drawDataPoint(x,y,temp_plot.m_shapeSize[i],color,temp_plot.m_shapeType[i])
                    else:
                        if not temp_plot.m_plotInstances.instance(i).isMissing(self.m_cIndex):
                            r=(temp_plot.m_plotInstances.instance(i).value(self.m_cIndex)-self.m_minC)/(self.m_maxC-self.m_minC)
                            r=r*240+15
                            color=Utils.rgb((int(r),150,int(255-r)))
                        else:
                            color="#708090"
                        if temp_plot.m_plotInstances.instance(i).isMissing(self.m_cIndex):
                            # if temp_plot.m_connecctPoints[i]:
                            self.drawDataPoint(x,y,temp_plot.m_shapeSize[i],color,Plot2D.MISSING_SHAPE.value)
                        else:
                            if temp_plot.m_shapeType[i] == Plot2D.CONST_AUTOMATIC_SHAPE:
                                # if temp_plot.m_connecctPoints[i]:
                                self.drawDataPoint(x,y,temp_plot.m_shapeSize[i],color,j)
                            else:
                                # if temp_plot.m_connecctPoints[i]:
                                self.drawDataPoint(x,y,temp_plot.m_shapeSize[i],color,temp_plot.m_shapeType[i])





    def drawDataPoint(self,x:float,y:float,size:int,color:str,shape:int):
        if size <= 0:
            size=1
        if shape != Plot2D.ERROR_SHAPE and shape != Plot2D.MISSING_SHAPE:
            shape=shape%5
        marker=self.m_markers.get(shape)
        self.axes.scatter(x,y,s=size,c=color,marker=marker)

    # def paintPoint(self):
    #     self.m_XaxisStart=189900
    #     self.m_XaxisEnd=325000
    #     self.m_YaxisStart=223957.0928571
    #     self.m_YaxisEnd=223957.1928571
    #     print("xStart: ",self.m_XaxisStart,"xEnd: ",self.m_XaxisEnd)
    #     print("yStart: ",self.m_YaxisStart,"yEnd: ",self.m_YaxisEnd)
    #     self.fig.subplots_adjust(top=0.95, bottom=0.1, left=0.2, right=0.95, hspace=0, wspace=0)
    #     self.paintAxis()
    #     self.showFrame(True)
    #     # x = np.arange(1, 5)
    #     # y = x
    #     # sValue = x * 10
    #     # self.axes.scatter(x, y, s=sValue, c='r', marker='^')
    #     self.axes.scatter(230000,223957.14285714287,s=10,c='r',marker='x')
    #     self.draw()

    decision_node = dict(boxstyle="sawtooth", fc="0.8")
    leaf_node = dict(boxstyle="round4", fc="0.8")
    arrow_args = dict(arrowstyle="<-")

    def get_num_leafs(self,mytree):
        '''
        获取叶子节点数
        '''
        num_leafs = 0
        first_str = list(mytree.keys())[0]
        second_dict = mytree[first_str]

        for key in second_dict.keys():
            if type(second_dict[key]).__name__ == 'dict':
                num_leafs += self.get_num_leafs(second_dict[key])
            else:
                num_leafs += 1

        return num_leafs

    def get_tree_depth(self,mytree):
        '''
        获取树的深度
        '''
        max_depth = 0
        first_str = list(mytree.keys())[0]
        second_dict = mytree[first_str]

        for key in second_dict.keys():
            # 如果子节点是字典类型，则该节点也是一个判断节点，需要递归调用
            # get_tree_depth()函数
            if type(second_dict[key]).__name__ == 'dict':
                this_depth = 1 + self.get_tree_depth(second_dict[key])
            else:
                this_depth = 1

            if this_depth > max_depth:
                max_depth = this_depth

        return max_depth

    def plot_node(self,ax, node_txt, center_ptr, parent_ptr, node_type):
        '''
            绘制带箭头的注解
        '''
        ax.annotate(node_txt, xy=parent_ptr, xycoords='axes fraction',
                    xytext=center_ptr, textcoords='axes fraction',
                    va="center", ha="center", bbox=node_type, arrowprops=self.arrow_args)

    def plot_mid_text(self,ax, center_ptr, parent_ptr, txt):
        '''
        在父子节点间填充文本信息
        '''
        x_mid = (parent_ptr[0] - center_ptr[0]) / 2.0 + center_ptr[0]
        y_mid = (parent_ptr[1] - center_ptr[1]) / 2.0 + center_ptr[1]

        ax.text(x_mid, y_mid, txt)



    def create_plot(self,in_tree):
        # fig = plt.figure(1, facecolor="white")
        # fig.clf()
        self.fig.subplots_adjust(top=0.8, bottom=0.2, left=0.2, right=0.8, hspace=0, wspace=0)
        ax_props = dict(xticks=[], yticks=[])
        # ax = plt.subplot(111, frameon=False, **ax_props)
        plot_tree=self.createPlotTree(in_tree)
        plot_tree(self.axes, in_tree, (0.5, 1.0), "")
        #     plot_node(ax, "a decision node", (0.5, 0.1), (0.1, 0.5), decision_node)
        #     plot_node(ax, "a leaf node", (0.8, 0.1), (0.3, 0.8), leaf_node)
        self.draw()

    def createPlotTree(self,in_tree):
        total_width = float(self.get_num_leafs(in_tree))
        total_depth = float(self.get_tree_depth(in_tree))
        x_off = -0.5 / total_width
        y_off = 1.0
        def plot_tree(ax, mytree, parent_ptr, node_txt):
            nonlocal x_off,y_off,total_depth,total_width

            num_leafs = self.get_num_leafs(mytree)

            first_str = list(mytree.keys())[0]
            center_ptr = (
            x_off + (1.0 + float(num_leafs)) / 2.0 / total_width, y_off)

            # 绘制特征值，并计算父节点和子节点的中心位置，添加标签信息
            self.plot_mid_text(ax, center_ptr, parent_ptr, node_txt)
            self.plot_node(ax, first_str, center_ptr, parent_ptr, self.decision_node)

            second_dict = mytree[first_str]
            # 采用的自顶向下的绘图，需要依次递减Y坐标
            y_off -= 1.0 / total_depth

            # 遍历子节点，如果是叶子节点，则绘制叶子节点，否则，递归调用self.plot_tree()
            for key in second_dict.keys():
                if type(second_dict[key]).__name__ == "dict":
                    plot_tree(ax, second_dict[key], center_ptr, str(key))
                else:
                    x_off += 1.0 / total_width
                    self.plot_mid_text(ax, (x_off, y_off), center_ptr, str(key))
                    self.plot_node(ax, second_dict[key], (x_off, y_off), center_ptr,self.leaf_node)

            # 在绘制完所有子节点之后，需要增加Y的偏移
            y_off += 1.0 / total_depth
        return plot_tree

class MatplotlibWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.initUi()
        self.m_plot2D=self.mpl  #type:MyMplCanvas

    def initUi(self):
        self.layout=QVBoxLayout(self)
        self.mpl=MyMplCanvas(self,width=5,height=4,dpi=100)
        # self.mpl.paintPoint()
        # dataList=np.array([[30,21,34,33,40,28,34,54],[57,48,35,45,47,29,29,36]])
        # colorList=['blue','red']
        # barWidth=60.625
        # self.mpl.paintRect(dataList,barWidth,colorList)
        # self.setXLimt(18,67,8)

        self.layout.addWidget(self.mpl)

    def setXLimt(self,left,right,len):
        Utils.debugOut("Xlimit_left:",left)
        Utils.debugOut("Xlimit_right:",right)
        Utils.debugOut("Xlimit_len:",len)
        midX=len/2
        mid=(left+right)/2
        ticks=[-0.5,midX-0.5,len-0.5]
        self.mpl.axes.set_xticks(ticks)
        left='%.2f'%left
        mid='%.2f'%mid
        right='%.2f'%right
        labelNumber=[left,mid,right]
        labels=[str(i) for i in labelNumber]
        self.mpl.axes.set_xticklabels(labels)
        self.mpl.draw()

    def clear(self):
        self.m_plot2D.clear()

    def createTree(self,dotty:str):
        d=ast.literal_eval(dotty)
        self.m_plot2D.create_plot(d)

#
# def retrieve_tree(i):
#     list_of_trees = [{'no surfacing': {0: 'no', 1: {'flippers': {0: 'no', 1: 'yes'}}}},
#                      {'no surfacing': {0: 'no', 1: {'flippers': {0: {'head': {0: 'no', 1: 'yes'}}, 1: 'no'}}}}
#                      ]
#     return list_of_trees[i]
#
# if __name__=="__main__":
#     app=QApplication(sys.argv)
#     win=MatplotlibWidget()
#     # mytree = retrieve_tree(1)
#     # mytree['no surfacing'][3] = "maybe"
#     mytree={"IncomeBracket":{"=0":"A","=1":"B","=2":"C","=3":{"FirstPurchase":{"<=200":"a",">200":"b"}},
#                              "=4":"E","=5":"F","=6":{"FirstPurchase":{"<=2003":"x",">2003":"y"}},
#                              "=7":"G"}}
#     win.m_plot2D.create_plot(mytree)
#     win.show()
#     sys.exit(app.exec_())

