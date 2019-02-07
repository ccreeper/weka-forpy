from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PluginManager import PluginManager
from Utils import Utils
import importlib

class PropertySheetPanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.m_env=self.width()
        self.m_Properties=None
        self.m_Methods=None
        self.m_Editors=[]
        self.m_Labels=[]        #type:List[QLabel]
        self.m_Views=[]     #type:List[QWidget]

    def setTarget(self,target:object):
        componentOffset=0
        layout=QFormLayout()

        self.setVisible(False)
        self.m_NumEditable=0
        self.m_Target=target
        #忽略类型，直接固定的接口，接口包括返回所有属性name的List和所有方法name的List
        self.m_Properties= target.getAllProperties()
        self.m_Methods=target.getAllMethods()
        propOrdering=[0]*len(self.m_Properties)
        for i in range(len(self.m_Properties)):
            propOrdering[i]=float("inf")
        sortedPropOrderings=Utils.sort(propOrdering)
        for i in range(len(self.m_Properties)):
            name=self.m_Properties[sortedPropOrderings[i]]
            try:
                property=getattr(target,self.m_Properties[sortedPropOrderings[i]])
            except AttributeError:
                continue
            label=QLabel(name)
            if type(property) is bool:
                view=QComboBox()
                view.addItems(['True','False'])
                if property:
                    view.setCurrentIndex(0)
                else:
                    view.setCurrentIndex(1)
            else:
                view=QLineEdit()
                view.setText(str(property))
            layout.addRow(label,view)
            self.m_Labels.append(label)
            self.m_Views.append(view)
        self.setLayout(layout)

    def setLayout(self, a0: 'QLayout'):
        super().setLayout(a0)
        self.layoutMgr=a0


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys


# class A():
#     properties=['number','flag']
#     methods=['Func']
#     def __init__(self):
#         self.number=5
#         self.flag=True

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
#     win.resize(500,500)
#     win.setTarget(a)
#     win.show()
#     sys.exit(app.exec_())
