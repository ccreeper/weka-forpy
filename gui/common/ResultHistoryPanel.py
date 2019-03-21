from typing import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Utils import Utils
from VisualizePanel import VisualizePanel
from Attributes import Attribute
from Instances import Instances,Instance
from classifiers.Classifier import Classifier


class ResultHistoryPanel(QListWidget):
    outtext_write_signal=pyqtSignal(str)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.m_SingleText=None      #type:QTextEdit
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.m_Results=dict()       #type:Dict[str,str]
        self.m_Objs=dict()              #type:Dict[str,object]
        self.m_SingleName=""
        # self.m_IsMenuClick=False
        self.itemClicked.connect(self.valueChanged)
        #菜单设置
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        self.createMenu()

    def generateMenu(self):
        # self.setMenuClickNow(True)
        # self.setMenu()
        self.setMenuEnable()
        action = self.m_Menu.exec_(self.cursor().pos())
        if action == self.showClassifierErrors:
            self.visualizeClassifierErrors(self.temp_vp)
        elif action == self.showVisualizeTree:
            pass
        else:
            return
        # self.m_Table.setMenuClickNow(False)

    def setMenuEnable(self):
        selectedNames=[i.text()  for i in self.selectedItems()]
        o=None      #type:List
        if selectedNames is not None and len(selectedNames) == 1:
            Utils.debugOut("history_name: ",selectedNames)
            o=self.getNamedObject(selectedNames[0])
        self.temp_vp=None        #type:VisualizePanel
        self.temp_trainHeader=None       #type:Instances
        self.temp_classifier=None        #type:Classifier
        self.temp_classAtt=None      #type:Attribute
        if o is not None:
            for i in range(len(o)):
                temp=o[i]
                if isinstance(temp,Classifier):
                    self.temp_classifier=temp
                elif isinstance(temp,Instances):
                    self.temp_trainHeader=temp
                elif isinstance(temp,VisualizePanel):
                    self.temp_vp=temp
                elif isinstance(temp,Attribute):
                    self.temp_classAtt=temp
        if self.temp_vp is not None:
            self.showClassifierErrors.setEnabled(True)
            if self.temp_vp.getXIndex() == 0 and self.temp_vp.getYIndex() == 1:
                self.temp_vp.setXIndex(self.temp_vp.getInstances().classIndex())
                self.temp_vp.setYIndex(self.temp_vp.getInstances().classIndex()-1)
        else:
            self.showClassifierErrors.setEnabled(False)

    def visualizeClassifierErrors(self,sp:VisualizePanel):
        if sp is not None:
            plotName=sp.getName()
            sp.setWindowTitle("Classifier Visualize: "+plotName)
        sp.draw()
        sp.show()


    def getNamedObject(self,name:str):
        v=self.m_Objs.get(name)
        return v

    def createMenu(self):
        self.m_Menu = QMenu()
        self.showClassifierErrors = self.m_Menu.addAction(u"Visualize classifier errors")
        self.showVisualizeTree = self.m_Menu.addAction(u"Visualize tree")

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
        if self.m_SingleText is not None:
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

