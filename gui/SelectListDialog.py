from SelectList import Ui_Dialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from typing import *
from Utils import Utils

class SelectListDialog(QMainWindow,Ui_Dialog):
    select_attributes_signal=pyqtSignal(list)
    def __init__(self,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selectBotton.clicked.connect(self.selectBtnClick)

    def setList(self,li:List):
        slm=QStringListModel()
        slm.setStringList(li)
        self.listView.setModel(slm)

    def selectBtnClick(self):
        res=[]
        reply=QMessageBox.question(self,"Confirm...","确认删除所选的 "+str(len(self.listView.selectedIndexes()))+" 个属性？",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if reply == QMessageBox.Yes:
            for i in self.listView.selectedIndexes():
                res.append(i.row()+1-len(res))
            self.select_attributes_signal.emit(res)
            self.close()

