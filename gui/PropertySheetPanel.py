from typing import *

from PyQt5.QtWidgets import *
from core.Tag import Tag

from core.Utils import Utils


class PropertySheetPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_env = self.width()
        self.m_Properties = None    #type:Dict
        self.m_Methods = None       #type:Dict
        self.m_Editors = []
        self.m_Labels = []  # type:List[QLabel]
        self.m_Views = []  # type:List[QWidget]

    def setTarget(self, target: object):
        if self.layout() is None:
            layout = QFormLayout()
            self.setLayout(layout)
        else:
            layout = self.layout()
        while layout.rowCount() > 0:
            layout.removeRow(0)
        self.m_Labels.clear()
        self.m_Views.clear()
        self.setVisible(False)
        self.m_NumEditable = 0
        self.m_Target = target
        # 忽略类型，直接固定的接口，接口包括返回所有属性name的List和所有方法name的List
        self.m_Properties = target.getAllProperties()       #type:Dict
        self.m_Methods = target.getAllMethods()         #type:Dict
        def setValue(name: str,attrType:type):
            if attrType is bool:
                def callSet(option:str):
                    if option.lower() == "true":
                        setattr(target,name,True)
                    else:
                        setattr(target,name,False)
            else:
                def callSet(option):
                    if option != "":
                        if attrType is int:
                            setattr(target, name, int(option))
                        elif attrType is float:
                            setattr(target,name,float(option))
            return callSet

        for name,value in self.m_Properties.items():
            val=None
            try:
                property = getattr(target, name)
                if value != "":
                    try:
                        val=getattr(target,value)
                    except AttributeError:
                        pass
            except AttributeError:
                continue

            # print("name:", name, "type:", type(property))
            label = QLabel(name)
            # func = setValue(name,type(property))
            if isinstance(property, bool):
                view = QComboBox()
                view.addItems(['False', 'True'])
                if property:
                    view.setCurrentIndex(1)
                else:
                    view.setCurrentIndex(0)
                # view.currentIndexChanged[str].connect(copy.deepcopy(func))
            elif val is not None:
                items=[]
                view=QComboBox()
                cur=i=0
                for item in val:
                    if isinstance(item,Tag):
                        items.append(item.getReadable())
                        if property == item.getID():
                            cur=i
                        i+=1
                view.addItems(items)
                view.setCurrentIndex(cur)
            else:
                view = QLineEdit()
                view.setText(str(value))
                # view.textChanged.connect(copy.deepcopy(func))
            layout.addRow(label, view)
            self.m_Labels.append(label)
            self.m_Views.append(view)
        self.setFixedHeight(40 * len(self.m_Properties))
        Utils.debugOut("layout row count:", layout.rowCount())
        self.repaint()
        self.show()

    def setLayout(self, a0: 'QLayout'):
        super().setLayout(a0)
        self.layoutMgr = a0

    def updateObject(self):
        for index in range(len(self.m_Labels)):
            labelName=self.m_Labels[index].text()
            setMethodName=self.m_Methods.get(labelName)
            if setMethodName is not None:
                try:
                    setMethod=getattr(self.m_Target,setMethodName)
                except AttributeError:
                    continue
                view=self.m_Views[index]
                if isinstance(view,QLineEdit):
                    setMethod(view.text())
                elif isinstance(view,QComboBox):
                    setMethod(view.currentIndex())

# Test
# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *
# import sys
#
#
# class A():
#     properties=['number','flag']
#     methods=['Func']
#     def __init__(self):
#         self.number=5
#         self.flag=True
#
#     def Func(self):
#         print("A")
#
#     def getAllProperties(self):
#         return self.properties
#
#     def getAllMethods(self):
#         return self.methods
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     a=A()
#     win = PropertySheetPanel()
#     win.setTarget(a)
#     win.show()
#     sys.exit(app.exec_())
