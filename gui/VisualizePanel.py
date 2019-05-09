from typing import *

from PyQt5.QtWidgets import *

from core.Attributes import Attribute
from core.Instances import Instances
from gui.PlotData2D import PlotData2D
from gui.designUI.VisualizePrint import Ui_Form


class VisualizePanel(QMainWindow,Ui_Form):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.m_plot=self.canvas
        self.m_plotName=self.relation_lab
        self.m_XCombo=self.x_comboBox
        self.m_YCombo=self.y_comboBox
        self.m_ColourCombo=self.c_comboBox
        self.m_SaveBtn=self.saveBtn
        self.m_preferredXDimension = None    #type:str
        self.m_preferredYDimension = None    #type:str
        self.m_preferredColourDimension = None   #type:str
        self.m_createShape=False
        self.m_plotInstances=None       #type:Instances
        self.m_shapePoints=None     #type:List[float]
        self.m_shapes=None      #type:List[List[float]]
        self.m_XCombo.currentIndexChanged[int].connect(self.XComboBoxChange)
        self.m_YCombo.currentIndexChanged[int].connect(self.YComboBoxChange)
        self.m_ColourCombo.currentIndexChanged[int].connect(self.ColourComboBoxChange)
        self.m_SaveBtn.clicked.connect(self.saveVisibleInstances)

        self.setFixedSize(self.width(),self.height())

    def XComboBoxChange(self,index:int):
        self.setXIndex(index)

    def YComboBoxChange(self,index:int):
        self.setYIndex(index)

    def ColourComboBoxChange(self,index:int):
        self.setCindex(index)

    def getXIndex(self):
        return self.m_XCombo.currentIndex()

    def getYIndex(self):
        return self.m_YCombo.currentIndex()

    def getName(self):
        return self.m_plotName

    def getInstances(self)->Instances:
        return self.m_plotInstances

    def setName(self,plotName:str):
        self.m_plotName=plotName

    def setXIndex(self,index:int):
        self.m_XCombo.setCurrentIndex(index)
        if index >= 0 and index < self.m_XCombo.count():
            self.m_xIndex=index
            self.m_plot.m_plot2D.setXindex(index)
            self.draw()
        else:
            raise Exception("x index is out of range!")

    def setYIndex(self,index:int):
        self.m_YCombo.setCurrentIndex(index)
        if index >= 0 and index < self.m_YCombo.count():
            self.m_yIndex=index
            self.m_plot.m_plot2D.setYindex(index)
            self.draw()
        else:
            raise Exception("y index is out of range!")

    def setCindex(self,index:int):
        self.m_cIndex=index
        self.m_plot.m_plot2D.setCindex(index)
        self.draw()

    def addPlot(self,newPlot:PlotData2D):
        if len(self.m_plot.m_plot2D.getPlots()) == 0:
            self.m_plot.m_plot2D.addPlot(newPlot)
            self.plotReset(newPlot.m_plotInstances,newPlot.getCindex())
        if self.m_plot.m_plot2D.getMasterPlot() is not None:
            self.setUpComboBoxes(newPlot.m_plotInstances)

    def plotReset(self,inst:Instances,cIndex:int):
        self.m_plotInstances=inst
        self.m_XCombo.setCurrentIndex(0)
        self.m_YCombo.setCurrentIndex(0)
        self.m_cIndex=cIndex
        self.cancelShapes()

    def cancelShapes(self):
        self.m_createShape=False
        self.m_shapePoints=None
        self.m_shapes=None

    def setUpComboBoxes(self,inst:Instances):
        XNames=[]
        YNames=[]
        CNames=[]
        for i in range(inst.numAttributes()):
            type=" ("+Attribute.typeToStringShort(inst.attribute(i))+")"
            XNames.append("X: "+inst.attribute(i).name()+type)
            YNames.append("Y: "+inst.attribute(i).name()+type)
            CNames.append("Colour: "+inst.attribute(i).name()+type)
        self.m_XCombo.addItems(XNames)
        self.m_YCombo.addItems(YNames)
        self.m_ColourCombo.addItems(CNames)
        self.m_XCombo.setCurrentIndex(0)
        self.m_YCombo.setCurrentIndex(1)
        self.m_ColourCombo.setCurrentIndex(inst.numAttributes()-1)

    def saveVisibleInstances(self):
        plots=self.m_plot.m_plot2D.getPlots()
        if plots is not None:
            master=plots[0]
            saveInsts=Instances(master.getPlotInstances())
            for i in range(1,len(plots)):
                temp=plots[i]
                addInsts=temp.getPlotInstances()
                for j in range(addInsts.numInstances()):
                    saveInsts.add(addInsts.instance(j))
            # for ins in saveInsts:
            #     for i in range(saveInsts.numAttributes()):
            #         print(",",ins.value(i),end="")
            #     print()
            # print(saveInsts.toArffString())
            filename = QFileDialog.getSaveFileName(self, '保存文件', '/', 'Arff data files(*.arff)')
            with open(filename[0], 'w') as f:
                text = saveInsts.toArffString()
                f.write(text)

    def draw(self):
        self.m_plot.m_plot2D.paintPoint()

# import sys
# from PyQt5.QtCore import *
# if __name__ == "__main__":
#     app=QApplication(sys.argv)
#     cgitb.enable(format='text')
#     sp=VisualizePanel()
#     sp.y_comboBox.addItems(['1','2','3'])
#     sp.show()
#     sys.exit(app.exec_())