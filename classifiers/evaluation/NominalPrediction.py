from typing import *

from Utils import Utils
from classifiers.evaluation.Prediction import Prediction


class NominalPrediction(Prediction):
    def __init__(self,actual:float,distribution:List,weight:float):
        if distribution is None:
            raise Exception("Null distribution in NominalPrediction.")
        self.m_Actual=actual
        self.m_Distribution=distribution[:]
        self.m_Weight=weight
        self.m_Predicted=Utils.missingValue()
        self.updatePredicted()

    def updatePredicted(self):
        predictedClass=-1
        bestProb=0
        for i in range(len(self.m_Distribution)):
            if self.m_Distribution[i]>bestProb:
                predictedClass=i
                bestProb=self.m_Distribution[i]
        if predictedClass != -1:
            self.m_Predicted=predictedClass
        else:
            self.m_Predicted=Utils.missingValue()

    def distribution(self):
        return self.m_Distribution

    def predicted(self):
        return self.m_Predicted

    def actual(self):
        return self.m_Actual

    def weight(self):
        return self.m_Weight