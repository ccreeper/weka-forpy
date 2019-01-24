from typing import *
class Option():
    s_descriptorCache=dict()  
    def __init__(self,description:str,name:str,numArguments:int,synopisis:str):
        self.m_Descipition=description
        self.m_Name=name
        self.m_NumArguments=numArguments
        self.m_Synopisis=synopisis

    def listOptionsForClassHierarchy(self):
