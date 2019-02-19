from classifiers.evaluation.Prediction import Prediction
from typing import *
import copy

class NumericPrediction(Prediction):
    def __init__(self,actual:float,predicted:float,weight:float=1,predInt:List[List]=None):
        if predInt is None:
            predInt=[[]]
        self.m_Actual=actual
        self.m_Predicted=predicted
        self.m_Weight=weight
        self.setPredictionIntervals(predInt)

    def setPredictionIntervals(self,predInt:List[List]):
        self.m_PredictionIntervals=copy.deepcopy(predInt)
