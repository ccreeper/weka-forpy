from PyQt5.QtWidgets import *
from Utils import Utils
import copy

class PropertySheetPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_env = self.width()
        self.m_Properties = None
        self.m_Methods = None
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
        self.m_Properties = target.getAllProperties()
        self.m_Methods = target.getAllMethods()

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

        for i in range(len(self.m_Properties)):
            name = self.m_Properties[i]
            try:
                property = getattr(target, name)
            except AttributeError:
                continue

            print("name:", name, "type:", type(property))
            label = QLabel(name)
            func = setValue(name,type(property))
            if isinstance(property, bool):
                view = QComboBox()
                view.addItems(['False', 'True'])
                if property:
                    view.setCurrentIndex(1)
                else:
                    view.setCurrentIndex(0)
                view.currentIndexChanged[str].connect(copy.deepcopy(func))
            else:
                view = QLineEdit()
                view.setText(str(property))
                view.textChanged.connect(copy.deepcopy(func))
            layout.addRow(label, view)
            self.m_Labels.append(label)
            self.m_Views.append(view)
        self.setFixedHeight(35 * len(self.m_Properties))
        Utils.debugOut("layout row count:", layout.rowCount())
        self.repaint()
        self.show()

    def setLayout(self, a0: 'QLayout'):
        super().setLayout(a0)
        self.layoutMgr = a0

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
