from typing import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ResultHistoryPanel(QListWidget):
    outtext_write_signal=pyqtSignal(str)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.m_SingleText=None      #type:QTextEdit
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.m_Results=dict()       #type:Dict[str,str]
        self.m_SingleName=""
        self.itemClicked.connect(self.valueChanged)


    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Delete:
            items=self.selectedItems()
            for item in items:
                self.removeItemWidget(self.takeItem(self.row(item)))

    def valueChanged(self,itemCurrent:QListWidgetItem):
        if len(self.selectedItems()) > 1:
            return
        if self.m_SingleText is not None:
            self.setSingle(itemCurrent.text())


    def setSingle(self,name:str):
        buff=self.m_Results.get(name)
        if buff is not None:
            self.m_SingleName=name
            self.outtext_write_signal.emit(buff)

    def addResult(self,name:str,result:str):
        nameCp=name
        i=0
        while nameCp in self.m_Results:
            nameCp=name+"_"+str(i)
            i+=1
        self.addItem(nameCp)
        self.m_Results.update({nameCp:result})

    def updateResult(self,name:str,result:str=None):
        buff=self.m_Results.get(name)
        if buff is None:
            return
        if result is not None:
            buff=result
            self.m_Results.update({name:result})
        if self.m_SingleName == name:
            self.outtext_write_signal.emit(buff)
        #TODO 更新separate window文本

# import sys
# if __name__=="__main__":
#     app=QApplication(sys.argv)
#     win=ResultHistoryPanel()
#     text=QTextEdit(win)
#     win.bindSingleText(text)
#     items=['a','b','c','d','e','f','g','h','i','j','k','l']
#     win.addItems(items)
#     win.show()
#     win.addResult('a','zxczxcxzczxcxcxzczxc')
#     win.setSingle('a')
#     sys.exit(app.exec_())

