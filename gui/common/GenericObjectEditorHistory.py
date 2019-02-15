from typing import *
import copy

class GenericObjectEditorHistory():
    MAX_HISTORY_COUNT=10
    def __init__(self):
        self.m_History=[]       #type:List

    def add(self,obj:object):
        obj=copy.deepcopy(obj)
        if obj in self.m_History:
            self.m_History.remove(obj)
        self.m_History.insert(0,obj)
        while len(self.m_History) > self.MAX_HISTORY_COUNT:
            self.m_History.pop()

