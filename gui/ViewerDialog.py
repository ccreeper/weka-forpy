from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Viewer import Ui_Form
from ArffPanel import ArffPanel
from Instances import Instances
from PyQt5.QtGui import *
import threading

class ViewerDialog(QMainWindow,Ui_Form):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.m_RelationNameLabel=self.relationName
        self.m_BaseTable=ArffPanel(self.viewTable)
        self.m_AddInsBtn=self.addInstance
        self.m_UndoBtn=self.Undo
        self.m_OkBtn=self.Ok
        self.m_CancelBtn=self.Cancel


    # def showDialog(self,inst:Instances):

    def setInstances(self,inst:Instances):
        self.m_BaseTable.setInstances(inst)

