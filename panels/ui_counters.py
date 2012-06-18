# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/counters.ui'
#
# Created: Mon Feb 21 12:00:07 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName("Panel")
        Panel.resize(589, 452)
        self.gridLayout = QtGui.QGridLayout(Panel)
        self.gridLayout.setObjectName("gridLayout")
        self.counts1 = HugeDisplay(Panel)
        self.counts1.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.counts1.setFont(font)
        self.counts1.setObjectName("counts1")
        self.gridLayout.addWidget(self.counts1, 0, 0, 1, 1)
        self.counts2 = HugeDisplay(Panel)
        self.counts2.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.counts2.setFont(font)
        self.counts2.setObjectName("counts2")
        self.gridLayout.addWidget(self.counts2, 1, 0, 1, 1)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(Panel)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.t_range = QtGui.QSpinBox(Panel)
        self.t_range.setObjectName("t_range")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.t_range)
        self.gridLayout.addLayout(self.formLayout, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(363, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.plot1 = TimeTracePlot(Panel)
        self.plot1.setMinimumSize(QtCore.QSize(350, 200))
        self.plot1.setObjectName("plot1")
        self.gridLayout.addWidget(self.plot1, 0, 1, 1, 1)
        self.plot2 = TimeTracePlot(Panel)
        self.plot2.setMinimumSize(QtCore.QSize(350, 200))
        self.plot2.setObjectName("plot2")
        self.gridLayout.addWidget(self.plot2, 1, 1, 1, 1)

        self.retranslateUi(Panel)
        QtCore.QObject.connect(self.t_range, QtCore.SIGNAL("valueChanged(int)"), self.plot1.set_display_time)
        QtCore.QObject.connect(self.t_range, QtCore.SIGNAL("valueChanged(int)"), self.plot2.set_display_time)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.counts1.setText(QtGui.QApplication.translate("Panel", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.counts2.setText(QtGui.QApplication.translate("Panel", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Panel", "time span [s] (0: all time)", None, QtGui.QApplication.UnicodeUTF8))

from chaco_plot import TimeTracePlot
from panel import HugeDisplay
