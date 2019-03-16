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
    m_defaultColorsName=["white","black","blue","red","cyan","grey_blue","pink","green","orange","light_pink"]
    m_markers={
        Plot2D.MISSING_SHAPE:"1",
        Plot2D.ERROR_SHAPE:"s",
        Plot2D.DIAMOND_SHAPE:"D",
        Plot2D.X_SHAPE:"x",
        Plot2D.PLUS_SHAPE:"+",
        Plot2D.TRIANGLEDOWN_SHAPE:"v",
        Plot2D.TRIANGLEUP_SHAPE:"^"
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
        self.fig.subplots_adjust(top=0.99, bottom=0.05, left=0.05, right=0.99, hspace=0, wspace=0)

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
        self.m_plots.append(newPlot)
        self.setXindex(self.m_xIndex)
        self.setYindex(self.m_yIndex)
        self.setCindex(self.m_cIndex)

    def setXindex(self,x:int):
        self.m_xIndex=x
        for i in range(len(self.m_plots)):
            self.m_plots[i].setXindex(self.m_xIndex)
        self.determineBounds()
        self.m_axisChanged=True
        self.paintPoint()

    def setYindex(self,y:int):
        self.m_yIndex=y
        for i in range(len(self.m_plots)):
            self.m_plots[i].setYindex(self.m_yIndex)
        self.determineBounds()
        self.m_axisChanged=True
        self.paintPoint()

    def setCindex(self,c:int):
        self.m_cIndex=c
        for i in range(len(self.m_plots)):
            self.m_plots[i].setCindex(self.m_cIndex)
        self.determineBounds()
        self.m_axisChanged=True
        self.paintPoint()

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
        self.fillLookup()
        self.paintPoint()

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
                        x=self.convertToPanelX(temp_plot.m_plotInstances.instance(i).value(self.m_xIndex))
                        y=self.convertToPanelY(temp_plot.m_plotInstances.instance(i).value(self.m_yIndex))
                        temp_plot.m_pointLookup[i][0]=x
                        temp_plot.m_pointLookup[i][1]=y




    def convertToPanelX(self,xval:float):
        temp=(xval-self.m_minX)/(self.m_maxX-self.m_minX)
        temp2=temp*(self.m_XaxisEnd-self.m_XaxisStart)
        temp2+=self.m_XaxisStart
        return temp2

    def convertToPanelY(self,yval:float):
        temp=(yval-self.m_minY)/(self.m_maxY-self.m_minY)
        temp2=temp*(self.m_YaxisEnd-self.m_YaxisStart)
        temp2=self.m_YaxisEnd-temp2
        return temp2

    def getMasterPlot(self):
        return self.m_masterPlot

    def showFrame(self,flag:bool):
        self.fig.gca().spines['top'].set_visible(flag)
        self.fig.gca().spines['bottom'].set_visible(flag)
        self.fig.gca().spines['left'].set_visible(flag)
        self.fig.gca().spines['right'].set_visible(flag)

    def paintRect(self,dataSet:np.ndarray,barWidth:int,isNumeric:bool=False,colorList:List[str]=("black")):
        # 生成数据
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
                a=self.axes.bar(x, dataSet[i],bottom=bottom,color=self.m_defaultColors.get(colorName),width=width)
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
        self.axes.set_ylim(0,maxHeight*1.1)
        # 显示范围
        #l=min+width*x-(max-min)/2
        #r=max+width*x-(max-min)/2
        # self.axes.set_xlim(11, 69)
        # self.axes.set_ylim(15, 400)
        self.draw()

    def paintPoint(self):
        self.fig.subplots_adjust(top=0.95, bottom=0.1, left=0.2, right=0.95, hspace=0, wspace=0)
        self.paintAxis()
        self.showFrame(True)
        if self.m_plotInstances is not None and self.m_plotInstances.numInstances() > 0\
            and self.m_plotInstances.numAttributes() > 0:
            self.paintAxis()
            self.paintData()



    def paintAxis(self):
        len = self.m_XaxisEnd-self.m_XaxisStart
        Xticks = [0.6, len/2, len-0.5]
        self.axes.set_xticks(Xticks)
        len = self.m_YaxisEnd-self.m_YaxisStart
        Yticks=[0.6, len/2, len-0.5]
        self.axes.set_yticks(Yticks)
        top = '%.2f' % self.m_YaxisEnd
        mid = '%.2f' % ((self.m_YaxisEnd+self.m_YaxisStart)/2)
        bottom = '%.2f' % self.m_YaxisStart
        labelNumber = [int(self.m_XaxisStart), int((self.m_XaxisEnd+self.m_XaxisStart)/2), int(self.m_YaxisEnd)]
        labels = [str(i) for i in labelNumber]
        self.axes.set_xticklabels(labels)
        labelNumber = [bottom,mid,top]
        labels = [str(i) for i in labelNumber]
        self.axes.set_yticklabels(labels)

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
                    x_range=int(x)-self.m_XaxisStart
                    y_range=int(y)-self.m_YaxisStart
                    if x_range >= 0 and y_range >= 0:
                        if self.m_drawnPoints[x_range][y_range] == i or \
                            self.m_drawnPoints[x_range][y_range] == 0 or\
                            temp_plot.m_shapeSize[i] == temp_plot.m_alwaysDisplayPointsOfThisSize or\
                            temp_plot.m_displayAllPoints:
                            if temp_plot.m_plotInstances.attribute(self.m_cIndex).isNominal():
                                if temp_plot.m_plotInstances.instance(i).isMissing(self.m_cIndex):
                                    color="#808080"
                                else:
                                    ind=int(temp_plot.m_plotInstances.instance(i).value(self.m_cIndex))
                                    color=self.m_colorList[i]
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
                                    color="#808080"
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
        if size == 0:
            size=1
        if shape != Plot2D.ERROR_SHAPE and shape != Plot2D.MISSING_SHAPE:
            shape=shape%5
        marker=self.m_markers.get(shape)
        self.axes.scatter(x,y,s=size,c=color,marker=marker)

    # def paintPoint(self):
    #     self.fig.subplots_adjust(top=0.95, bottom=0.1, left=0.2, right=0.95, hspace=0, wspace=0)
    #     self.paintAxis()
    #     self.showFrame(True)
    #     x = np.arange(1, 5)
    #     y = x
    #     sValue = x * 10
    #     self.axes.scatter(x, y, s=sValue, c='r', marker='^')
    #     self.draw()

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
        self.mpl.axes.cla()
        self.mpl.axes.set_xticks([])
        self.mpl.axes.set_yticks([])

    def addPlot(self,newPlot:PlotData2D):
        if len(self.m_plot2D.getPlots()) == 0:
            self.m_plot2D.addPlot(newPlot)
            #TODO m_classPanel???

# if __name__=="__main__":
#     app=QApplication(sys.argv)
#     win=MatplotlibWidget()
#     win.show()
#     sys.exit(app.exec_())

