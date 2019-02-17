from typing import *
from OptionHandler import OptionHandler
from Instances import Instances

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