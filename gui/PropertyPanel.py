from GenericObjectEditor import GenericObjectEditor,GOEPanel
from Main import Ui_MainWindow
from TreeNodeButton import TreeNodeButton
from PyQt5.QtCore import *
from typing import *
#TODO
class PropertyPanel():
    def __init__(self,win:Ui_MainWindow,pe:GenericObjectEditor):
        self.m_Editor=pe
        self.m_PD=None                  #type:GOEPanel
        self.m_ChooseBut=win.choose_classifier      #type:TreeNodeButton
        self.m_OptionBut=win.option_classifier
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

