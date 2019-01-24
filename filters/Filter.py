from typing import *
from Instances import Instances

class Filter():
    def __init__(self):
        self.m_OutputFormat=None #type:Instances
        #TODO Queue
        self.m_InputFormat=None #type:Instances
        self.m_NewBatch=True
        self.m_FirstBatchDone=False
        self.m_Debug=False
        self.m_DoNotCheckCapabilities=False

    def isNewBatch(self):
        return self.m_NewBatch

    def isFirstBatchDone(self):
        return self.m_FirstBatchDone

