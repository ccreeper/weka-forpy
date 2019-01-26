from typing import *
class Option():
    #{type:pro}
    s_descriptorCache=dict()
    def __init__(self,description:str,name:str,numArguments:int,synopisis:str):
        self.m_Descipition=description
        self.m_Name=name
        self.m_NumArguments=numArguments
        self.m_Synopisis=synopisis

    # @classmethod
    # def listOptionsForClassHierarchy(cls,childClazz:type,oldestAncestorClazz:type):
    #     results=
    #
    # @classmethod
    # def listOptionsForClass(cls,clazz:type):
    #     results=[]
    #     allMethods=[]
    #     cls.addMethodsToList(clazz,allMethods)
    #     interfaces=
    #
    # @classmethod
    # def addMethodsToList(cls,clazz:type,methList:List):
    #     methods=clazz.getMethods()
    #     for m in methods:
    #         methList.append(m)

