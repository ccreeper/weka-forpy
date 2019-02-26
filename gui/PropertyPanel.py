from GenericObjectEditor import GenericObjectEditor,GOEPanel
from TreeNodeButton import TreeNodeButton
from typing import *

class PropertyPanel():
    def __init__(self,tab,pe:GenericObjectEditor):
        self.m_Editor=pe
        self.m_PD=None                  #type:GOEPanel
        self.m_ChooseBut=tab.getChooseBut()      #type:TreeNodeButton
        self.m_OptionBut=tab.getOptionBut()
        self.m_OptionBut.setStyleSheet("text-align:left")
        self.m_OptionBut.setFlat(True)
        self.m_ChooseBut.clicked.connect(self.chooseClick)
        self.m_OptionBut.clicked.connect(self.optionClick)
        self.m_Editor.classifier_changed.connect(self.classifierChangedEvent)

    def chooseClick(self):

        self.m_ChooseBut.setTree(self.m_Editor.getTreeMenu())
        self.m_ChooseBut.showPopupMenu()

    def optionClick(self):
        if self.m_PD is None:
            self.m_PD=self.m_Editor.getCustomEditor()
        print("Backup:",self.m_Editor.m_Backup)
        print("Value:",self.m_Editor.getValue())
        self.m_Editor.setValue(self.m_Editor.getValue())
        self.m_PD.adjustSize()
        self.m_PD.show()

    def classifierChangedEvent(self,clsName):
        self.m_OptionBut.setText(clsName)
        self.m_ChooseBut.hidePopupMenu()

    def addToHistory(self,obj:object=None):
        if obj is None:
            return self.addToHistory(self.m_Editor.getValue())
        if isinstance(self.m_Editor,GenericObjectEditor) and obj is not None:
            self.m_Editor.getHistory().add(obj)
            return True
        return False

