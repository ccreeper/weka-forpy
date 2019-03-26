from typing import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ResultHistoryPanel(QListWidget):
    outtext_write_signal=pyqtSignal(str)
    menu_expand_signal=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.m_Results=dict()       #type:Dict[str,str]
        self.m_Objs=dict()              #type:Dict[str,object]
        self.m_SingleName=""
        # self.m_IsMenuClick=False
        self.itemClicked.connect(self.valueChanged)
        #菜单设置
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        # self.createMenu()
        self.tree_mp=None

    def generateMenu(self):
        # self.setMenuClickNow(True)
        # self.setMenu()
        # self.setMenuEnable()
        # action = self.m_Menu.exec_(self.cursor().pos())
        # if action == self.showClassifierErrors:
        #     self.visualizeClassifierErrors(self.temp_vp)
        # elif action == self.showVisualizeTree:
        #     self.visualizeTree(self.temp_grph)
        # else:
        #     return
        self.menu_expand_signal.emit()
        # self.m_Table.setMenuClickNow(False)

    def getNamedObject(self,name:str):
        v=self.m_Objs.get(name)
        return v

    # def createMenu(self):
    #     self.m_Menu = QMenu()
    #     self.showClassifierErrors = self.m_Menu.addAction(u"Visualize classifier errors")
    #     self.showVisualizeTree = self.m_Menu.addAction(u"Visualize tree")

    # def setMenuClickNow(self,flag:bool):
    #     self.m_IsMenuClick=flag

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Delete:
            items=self.selectedItems()
            for item in items:
                self.removeItemWidget(self.takeItem(self.row(item)))

    def valueChanged(self,itemCurrent:QListWidgetItem):
        if len(self.selectedItems()) > 1:
            return
        self.setSingle(itemCurrent.text())

    def addObject(self,name:str,o:object):
        nameCopy=name
        i=0
        while nameCopy in self.m_Objs:
            nameCopy=name+'_'+i
            i+=1
        self.m_Objs.update({nameCopy:o})

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

