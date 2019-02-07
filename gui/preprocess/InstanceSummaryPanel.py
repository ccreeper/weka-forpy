from Instances import Instances

from gui.designUI.Main import Ui_MainWindow


class InstanceSummaryPanel():
    def __init__(self,ui:Ui_MainWindow):
        self.m_RelationNameLab=ui.name_lab
        self.m_NumInstancesLab=ui.instance_lab
        self.m_NumAttributesLab=ui.attr_lab
        self.m_sumOfWeightsLab=ui.weight_lab

    def setInstance(self,inst:Instances):
        self.m_Instance=inst
        self.m_RelationNameLab.setText(inst.m_RelationName)
        self.m_NumInstancesLab.setText(str(inst.numInstances()))
        self.m_NumAttributesLab.setText(str(inst.numAttributes()))
        self.m_sumOfWeightsLab.setText(str(round(inst.sumOfWeight(),3)))



