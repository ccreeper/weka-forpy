from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import *
from Instances import Instances,Instance
from Utils import Utils

class InserInstanceDialog(QDialog):

    submit_signal=pyqtSignal(Instance,int)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新的实例")

    def setAttributes(self,inst:Instances,pos:int=-1):
        flo=QFormLayout()
        flo.setLabelAlignment(Qt.AlignRight)
        flo.setContentsMargins(20,20,20,20)
        flo.setSpacing(15)
        self.m_Instance=inst
        self.m_WidgetList=[]
        self.m_InsertPos=pos
        for i in range(inst.numAttributes()):
            attr=inst.attribute(i)
            label=QLabel(attr.name())
            if attr.isNominal():
                edit=QComboBox()
                edit.addItem("")
                edit.addItems(attr.values())
            elif attr.isNumeric():
                edit=QLineEdit()
                edit.setPlaceholderText("输入数字")
                pDoubleValidator=QDoubleValidator(self)
                edit.setValidator(pDoubleValidator)
            else:
                edit=QLineEdit()
            self.m_WidgetList.append(edit)
            flo.addRow(label,edit)
        hlayout=QHBoxLayout()
        submit=QPushButton("提交")
        submit.clicked.connect(self.submitClick)
        cancel=QPushButton("取消")
        cancel.clicked.connect(self.close)
        hlayout.addWidget(submit)
        hlayout.addWidget(cancel)
        widget=QWidget()
        widget.setLayout(hlayout)
        flo.addRow(widget)
        self.setLayout(flo)

    def submitClick(self):
        data=[]
        for i in range(self.m_Instance.numAttributes()):
            widget=self.m_WidgetList[i]
            if isinstance(widget,QComboBox):
                if widget.currentText() == "":
                    data.append(None)
                else:
                    data.append(widget.currentText())
            elif isinstance(widget,QLineEdit):
                if widget.text() == "":
                    data.append(None)
                elif isinstance(widget.validator(),QDoubleValidator):
                    data.append(float(widget.text()))
                else:
                    data.append(widget.text())
        newInstance = self.m_Instance.createInstance(data)
        self.submit_signal.emit(newInstance,self.m_InsertPos)
        self.close()