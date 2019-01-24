
import time
from functools import *

class DateAttributeInfo():
    def __init__(self,dateFormat:str=None):
        if dateFormat:
            self.m_DateFormat=partial(time.strftime,dateFormat)
        else:
            self.m_DateFormat=partial(time.strftime,"%Y-%m-%d'T'%H:%M:%S")


class NominalAttributeInfo():
    def __init__(self,attrValue:list=None):
        self.m_Values = []
        self.m_Hashtable = dict()
        if attrValue!=None:
            for i in range(len(attrValue)):
                store=str(attrValue[i])
                self.m_Values.append(store)
                self.m_Hashtable.update({store:i})


