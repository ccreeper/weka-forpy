# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SelectList.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(331, 470)
        self.listView = QtWidgets.QListView(Dialog)
        self.listView.setGeometry(QtCore.QRect(10, 10, 311, 411))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.listView.setFont(font)
        self.listView.setObjectName("listView")
        self.selectBotton = QtWidgets.QPushButton(Dialog)
        self.selectBotton.setGeometry(QtCore.QRect(40, 430, 93, 28))
        self.selectBotton.setObjectName("selectBotton")
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setGeometry(QtCore.QRect(200, 430, 93, 28))
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(Dialog)
        self.cancelButton.clicked.connect(Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.selectBotton.setText(_translate("Dialog", "Select"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))

