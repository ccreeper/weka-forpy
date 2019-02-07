from Instances import Instances
from core.OptionHandler import OptionHandler
from queue import Queue
from queue import Queue

from Instances import Instances

from core.OptionHandler import OptionHandler


class Filter():
    m_Methods = []
    def __init__(self):
        self.m_OutputFormat=None #type:Instances
        self.m_OutputQueue=Queue()
        self.m_InputFormat=None #type:Instances
        self.m_NewBatch=True
        self.m_FirstBatchDone=False
        self.m_Debug=False
        self.m_DoNotCheckCapabilities=False

    def isNewBatch(self):
        return self.m_NewBatch

    def isFirstBatchDone(self):
        return self.m_FirstBatchDone

    @classmethod
    def getMethods(cls):
        return cls.m_Methods

    def setInputFormat(self,instanceInfo:Instances):
        self.m_InputFormat=instanceInfo.stringFreeStructure()
        self.m_OutputFormat=None
        self.m_OutputQueue=Queue()
        self.m_NewBatch=True
        self.m_FirstBatchDone=False
        return False

    def setOutputFormat(self, outputFormat: Instances):
        if outputFormat is not None:
            self.m_OutputFormat = outputFormat.stringFreeStructure()

            relationName = outputFormat.relationName() + "-" +self.__class__.__name__
            if isinstance(self,OptionHandler):
                options=self.getOptions()
                for option in options:
                    relationName+=option.strip()
            self.m_OutputFormat.setRelationName(relationName)
        else:
            self.m_OutputFormat=None
        self.m_OutputQueue=Queue()

