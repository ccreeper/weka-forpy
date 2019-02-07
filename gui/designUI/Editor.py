# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Editor.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(484, 560)
        self.classNameLabel = QtWidgets.QLabel(Form)
        self.classNameLabel.setGeometry(QtCore.QRect(10, 10, 72, 15))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.classNameLabel.setFont(font)
        self.classNameLabel.setObjectName("classNameLabel")
        self.propertyWidget = PropertySheetPanel(Form)
        self.propertyWidget.setGeometry(QtCore.QRect(10, 40, 461, 451))
        self.propertyWidget.setObjectName("propertyWidget")
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(90, 510, 321, 30))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(120)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.okBtn.setObjectName("okBtn")
        self.horizontalLayout.addWidget(self.okBtn)
        self.cancelBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.cancelBtn.setObjectName("cancelBtn")
        self.horizontalLayout.addWidget(self.cancelBtn)

        self.retranslateUi(Form)
        self.cancelBtn.clicked.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.classNameLabel.setText(_translate("Form", "TextLabel"))
        self.okBtn.setText(_translate("Form", "OK"))
        self.cancelBtn.setText(_translate("Form", "Cancel"))

from PropertySheetPanel import PropertySheetPanel

