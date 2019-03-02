from AbstractPlotInstances import AbstractPlotInstances
from typing import *
from clusterers.Clusterer import Clusterer
from clusterers.ClusterEvaluation import ClusterEvaluation

class ClustererAssignmentsPlotInstances(AbstractPlotInstances):
    def setClusterer(self,value:Clusterer):
        self.m_Clusterer=value

    def setClusterEvaluation(self,value:ClusterEvaluation):
        self.m_Evaluation=value
