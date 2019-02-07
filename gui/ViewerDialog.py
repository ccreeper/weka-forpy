from Instances import Instances
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui.designUI.Viewer import Ui_Form
from gui.preprocess.ArffPanel import ArffPanel


class ViewerDialog(QMainWindow,Ui_Form):
    class DialogResult():...
    APPROVE_OPTION=DialogResult()
    CANCEL_OPTION=DialogResult()

    close_signal=pyqtSignal(Instances)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.m_RelationNameLabel=self.relationName
        self.m_BaseTable=ArffPanel(self.viewTable)
        self.m_AddInsBtn=self.addInstance
        self.m_UndoBtn=self.Undo
        self.m_OkBtn=self.Ok
        self.m_CancelBtn=self.Cancel
        self.m_Result=self.CANCEL_OPTION
        self.attachListener()

    def attachListener(self):
        self.m_OkBtn.clicked.connect(self.okButtonClick)
        self.m_UndoBtn.clicked.connect(self.undoButtonClick)
        self.m_BaseTable.state_changed_signal.connect(self.setButton)
        self.m_AddInsBtn.clicked.connect(self.addInstanceClick)

    def setInstances(self,inst:Instances):
        self.m_RelationNameLabel.setText(inst.relationName())
        self.m_BaseTable.setInstances(inst)
        self.setButton()

    def getInstance(self):
        return self.m_BaseTable.getInstance()

    def okButtonClick(self):
        self.m_Result=self.APPROVE_OPTION
        self.close()

    def undoButtonClick(self):
        self.m_BaseTable.undo()

    def closeEvent(self, a0: QCloseEvent):
        if self.m_Result == ViewerDialog.APPROVE_OPTION:
            inst=self.getInstance()
            self.close_signal.emit(inst)

    def addInstanceClick(self):
        self.m_BaseTable.addInstance()

    def setButton(self):
        self.m_UndoBtn.setEnabled(self.m_BaseTable.canUndo())