from typing import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from gui.designUI.SelectList import Ui_Dialog


class SelectListDialog(QMainWindow,Ui_Dialog):
    select_attributes_signal=pyqtSignal(list)
    def __init__(self,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selectBotton.clicked.connect(self.selectBtnClick)
        self.m_Selection=[]

    def setList(self,li:List):
        slm=QStringListModel()
        slm.setStringList(li)
        self.listView.setModel(slm)

    def isSelectionEmpty(self):
        return len(self.m_Selection) == 0

    def getSelectedIndices(self)->List:
        return self.m_Selection

    def isSelectedIndex(self,index:int):
        return index in self.m_Selection

    def selectBtnClick(self):
        for i in self.listView.selectedIndexes():
            self.m_Selection.append(i.row())
        self.select_attributes_signal.emit(self.m_Selection)
        self.close()

