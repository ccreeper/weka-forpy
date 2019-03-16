# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VisualizePrint.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(865, 535)
        self.canvas = MatplotlibWidget(Form)
        self.canvas.setGeometry(QtCore.QRect(20, 90, 821, 431))
        self.canvas.setObjectName("canvas")
        self.relation_lab = QtWidgets.QLabel(Form)
        self.relation_lab.setGeometry(QtCore.QRect(20, 70, 72, 15))
        self.relation_lab.setObjectName("relation_lab")
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(20, 20, 821, 31))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.x_comboBox = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_comboBox.sizePolicy().hasHeightForWidth())
        self.x_comboBox.setSizePolicy(sizePolicy)
        self.x_comboBox.setObjectName("x_comboBox")
        self.horizontalLayout.addWidget(self.x_comboBox)
        self.y_comboBox = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_comboBox.sizePolicy().hasHeightForWidth())
        self.y_comboBox.setSizePolicy(sizePolicy)
        self.y_comboBox.setObjectName("y_comboBox")
        self.horizontalLayout.addWidget(self.y_comboBox)
        self.horizontalLayout.setStretch(0, 4)
        self.horizontalLayout.setStretch(1, 5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.relation_lab.setText(_translate("Form", "TextLabel"))

from MatplotlibWidget import MatplotlibWidget
