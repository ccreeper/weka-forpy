from typing import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ResultHistoryPanel(QListWidget):
    def __init__(self,text:QTextEdit,parent=None):
        super().__init__(parent)
        self.m_SingleText=text
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
            self.m_SingleText.setText(buff)

    def addResult(self,name:str,result:str):
        nameCp=name
        i=0
        while nameCp in self.m_Results:
            nameCp=name+"_"+str(i)
            i+=1
        self.addItem(nameCp)
        self.m_Results.update({nameCp:result})

    def updateResult(self,name:str):
        buff=self.m_Results.get(name)
        if buff is None:
            return
        if self.m_SingleName == name:
            self.m_SingleText.setText(buff)
        #TODO 更新separate window文本

# import sys
# if __name__=="__main__":
#     app=QApplication(sys.argv)
#     text=QTextEdit()
#     win=ResultHistoryPanel(text)
#     items=['a','b','c','d','e','f','g','h','i','j','k','l']
#     win.addItems(items)
#     win.show()
#     sys.exit(app.exec_())

