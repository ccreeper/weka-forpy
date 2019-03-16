from typing import *
from VisualizePrint import Ui_Form
from Instances import Instances,Instance
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PlotData2D import PlotData2D

class VisualizePanel(QWidget,Ui_Form):
    def __init__(self,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.m_plot=self.canvas
        self.m_plotName=self.relation_lab
        self.m_XCombo=self.x_comboBox
        self.m_YCombo=self.y_comboBox

    def setName(self,plotName:str):
        self.m_plotName=plotName

    def addPlot(self,newPlot:PlotData2D):
        self.m_plot.addPlot(newPlot)
        if self.m_plot.m_plot2D.getMasterPlot() is not None:
            #TODO 下拉选框初始化

