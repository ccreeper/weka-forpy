from typing import *

class PerformanceStats():
    def __init__(self):
        self.reset()

    def reset(self):
        self.m_NumQueries=0
        self.m_SumP=self.m_SumSqP=self.m_PointCount=0
        self.m_MinP=float("inf")
        self.m_MaxP=float("-inf")
        self.m_SumC=self.m_SumSqC=self.m_CoordCount=0
        self.m_MinC=float("inf")
        self.m_MaxC=float("-inf")

    def searchStart(self):
        self.m_PointCount=0
        self.m_CoordCount=0

    def incrPointCount(self):
        self.m_PointCount+=1

    def incrCoordCount(self):
        self.m_CoordCount+=1
