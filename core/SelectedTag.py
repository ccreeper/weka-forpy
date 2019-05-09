from typing import *

from core.Tag import Tag


class SelectedTag():
    def __init__(self, tagID:int, tags:List[Tag]):
        ID=set()
        IDStr=set()
        for i in range(len(tags)):
            newID=tags[i].getID()
            if newID not in ID:
                ID.add(newID)
            IDString=tags[i].getIDStr()
            if IDString not in IDStr:
                IDStr.add(IDString)
        for i in range(len(tags)):
            if tags[i].getID() == tagID:
                self.m_Selected=i
                self.m_Tags=tags
                return

    def __str__(self):
        return str(self.getSelectedTag())

    def getSelectedTag(self)-> Tag:
        return self.m_Tags[self.m_Selected]

    def getTags(self):
        return self.m_Tags