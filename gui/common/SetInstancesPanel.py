import arff
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from core.Attributes import Attribute
from core.Instances import Instances
from gui.designUI.TestInstance import Ui_Form


class SetInstancesPanel(QWidget,Ui_Form):
    NO_CLASS="No class"
    NO_SOURCE="None"
    combobox_changed_signal = pyqtSignal(int)
    def __init__(self,showZeroInstancesAsUnknown:bool=False,showClassComboBox:bool=False,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.setWindowTitle("Test Instances")
        self.setFixedSize(self.width(),self.height())
        self.m_OpenFileBut=self.open_btn
        self.m_CloseBut=self.close_btn
        self.m_RelationNameLab=self.name_lab
        self.m_NumInstancesLab=self.instance_lab
        self.m_NumAttributesLab=self.attr_lab
        self.m_sumOfWeightsLab=self.weight_lab
        self.m_Instances=None           #type:Instances
        self.m_ClassComboBox=self.class_combobox        #type:QComboBox
        self.m_ClassComboBox.setEnabled(showClassComboBox)

        self.m_showZeroInstancesAsUnknown=showZeroInstancesAsUnknown
        self.m_showClassComboBox=showClassComboBox
        self.m_OpenFileBut.clicked.connect(self.setInstancesFromFile)
        self.m_CloseBut.clicked.connect(self.close)
        self.m_ClassComboBox.currentIndexChanged.connect(self.comboBoxChanged)


    def setInstancesFromFile(self):
        filename = QFileDialog.getOpenFileName(self, '选择文件', '/','Arff data files(*.arff);;CSV data files(*.csv)')
        file = open(filename[0], 'rb')
        with file:
            s = file.read().decode('utf-8')
        data = arff.loads(s)
        print(data)
        inst = Instances(data)
        self.setInstances(inst)

    def setInstances(self,inst:Instances):
        self.m_Instances=inst
        self.m_RelationNameLab.setText(inst.relationName())
        self.m_NumAttributesLab.setText(str(inst.numAttributes()))
        self.m_NumInstancesLab.setText(str(inst.numInstances()))
        self.m_sumOfWeightsLab.setText(str(inst.sumOfWeight()))
        if self.m_showClassComboBox:
            self.m_ClassComboBox.clear()
            self.m_ClassComboBox.addItem(self.NO_CLASS)
            for i in range(inst.numAttributes()):
                att=inst.attribute(i)
                type = "(" + Attribute.typeToStringShort(att.type()) + ")"
                name = att.name()
                self.m_ClassComboBox.addItem(type+" "+name)
            if inst.classIndex() == -1:
                self.m_ClassComboBox.setCurrentIndex(inst.numAttributes())
            else:
                self.m_ClassComboBox.setCurrentIndex(inst.classIndex()+1)

    def comboBoxChanged(self):
        if self.m_Instances is not None:
            if self.m_Instances.numAttributes() >= self.m_ClassComboBox.currentIndex():
                self.m_Instances.setClassIndex(self.m_ClassComboBox.currentIndex()-1)
                self.combobox_changed_signal.emit(self.getClassIndex())

    def getClassIndex(self):
        return self.m_ClassComboBox.currentIndex()-1

    def getInstances(self):
        return self.m_Instances