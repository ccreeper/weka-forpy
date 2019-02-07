import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
import numpy as np
from typing import *
from core.Utils import Utils

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
        self.fig.subplots_adjust(top=0.99, bottom=0.1, left=0.01, right=0.99, hspace=0, wspace=0)

        #去边框
        self.fig.gca().spines['top'].set_visible(False)
        self.fig.gca().spines['bottom'].set_visible(False)
        self.fig.gca().spines['left'].set_visible(False)
        self.fig.gca().spines['right'].set_visible(False)

        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    #
    # def paintGraphics(self):
    #     # 生成数据
    #     # x = np.linspace(15, 65, 8)
    #     # y1 = np.random.randint(15, 65, 8)
    #     # y2 = np.random.randint(15, 65, 8)
    #     # 堆积柱状图
    #     #width=(max-min)/(x-1)
    #     x=np.arange(8)
    #     data = np.array([15, 20, 18, 25,15, 20, 18, 25])
    #     data2 = np.array([15, 20, 18, 25,15, 20, 18, 25])
    #     a1=self.axes.bar(x, data, color='r',width=1)
    #     a2=self.axes.bar(x, data2, bottom=data, color='g',width=1)
    #     for b in range(len(a2)):
    #         h=a2[b].get_height()+a1[b].get_height()
    #         self.axes.text(a2[b].get_x()+a2[b].get_width()/2, h,"%d"%int(h),ha='center',va='bottom')
    #     self.axes.set_yticks([])
    #     self.axes.set_xticks([-0.5,3.5,7.5])
    #     self.axes.set_xticklabels(['a','b','c'])
    #     # 显示范围
    #     #l=min+width*x-(max-min)/2
    #     #r=max+width*x-(max-min)/2
    #     # self.axes.set_xlim(11, 69)
    #     # self.axes.set_ylim(15, 200)
    #     self.draw()

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




class MatplotlibWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        self.layout=QVBoxLayout(self)
        self.mpl=MyMplCanvas(self,width=5,height=4,dpi=100)
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
        midLabel=(left+right)/2
        ticks=[-0.5,midX-0.5,len-0.5]
        self.mpl.axes.set_xticks(ticks)
        labelNumber=[left,midLabel,right]
        labels=[str(i) for i in labelNumber]
        self.mpl.axes.set_xticklabels(labels)
        self.mpl.draw()

    def clear(self):
        self.mpl.axes.cla()
        self.mpl.axes.set_xticks([])
        self.mpl.axes.set_yticks([])

# if __name__=="__main__":
#     app=QApplication(sys.argv)
#     win=MatplotlibWidget()
#     win.show()
#     sys.exit(app.exec_())

