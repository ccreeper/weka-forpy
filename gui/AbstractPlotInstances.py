from typing import *
from OptionHandler import OptionHandler
from Instances import Instances,Instance
from PlotData2D import PlotData2D

class AbstractPlotInstances(OptionHandler):
    def __init__(self):
        self.initialize()


    def initialize(self):
        self.m_Instances=None       #type:Instances
        self.m_PlotInstances=None   #type:Instances
        self.m_FinishUpCalled=False

    def setUp(self):
        self.m_FinishUpCalled=False
        self.determineFormat()

    def determineFormat(self):pass

    def setInstances(self,value:Instances):
        self.m_Instances=value

    def getPlotInstances(self):
        if not self.m_FinishUpCalled:
            self.finishUp()
        return self.m_PlotInstances

    def finishUp(self):
        self.m_FinishUpCalled=True

    def canPlot(self,setup:bool):
        try:
            if setup:
                self.setUp()
            return self.getPlotInstances().numInstances()>0
        except Exception:
            return False

    def getPlotData(self,name:str)->PlotData2D:
        if not self.m_FinishUpCalled:
            self.finishUp()
        return self.createPlotData(name)

    def createPlotData(self,name:str)->PlotData2D:...