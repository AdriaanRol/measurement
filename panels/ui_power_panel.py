# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'power.ui'
#
# Created: Wed Mar 02 13:31:16 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName("Panel")
        Panel.resize(247, 184)
        self.gridLayout = QtGui.QGridLayout(Panel)
        self.gridLayout.setObjectName("gridLayout")
        self.power = HugeDisplay(Panel)
        self.power.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.power.setFont(font)
        self.power.setObjectName("power")
        self.gridLayout.addWidget(self.power, 0, 0, 1, 2)
        self.label = QtGui.QLabel(Panel)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.correction_factor = QtGui.QDoubleSpinBox(Panel)
        self.correction_factor.setMinimum(-1.0)
        self.correction_factor.setMaximum(100.0)
        self.correction_factor.setProperty("value", 1.0)
        self.correction_factor.setObjectName("correction_factor")
        self.gridLayout.addWidget(self.correction_factor, 1, 1, 1, 1)

        self.retranslateUi(Panel)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.power.setText(QtGui.QApplication.translate("Panel", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Panel", "P(actual)/P(measured)", None, QtGui.QApplication.UnicodeUTF8))

from panel import HugeDisplay
