from Utils import Utils
from typing import *

class GenericObjectEditorHistory():
    def __init__(self):
        self.m_History=[]

class GenericObjectEditor():
    def __init__(self,canChangeClassInDialog:bool=False):
        self.m_canChangeClassInDialog=canChangeClassInDialog
        self.m_History=GenericObjectEditorHistory()

    #TODO 直接对每个类生成代替
    # def setClassType(self,tp:type):
    #     self.m_ClassType=tp
    #     self.m_ObjectNames=
    #
    # def getClassFromProperties(self):
    #     hpps=dict()
    #     className=self.m_ClassType.__name__
    #     cls=