# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'counts_v2.ui'
#
# Created: Thu Nov 17 18:47:34 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName(_fromUtf8("Panel"))
        Panel.resize(495, 374)
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Panel)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.counts = QtGui.QLabel(Panel)
        self.counts.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.counts.setFont(font)
        self.counts.setText(QtGui.QApplication.translate("Panel", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.counts.setObjectName(_fromUtf8("counts"))
        self.verticalLayout.addWidget(self.counts)
        self.plot = TimeTracePlot(Panel)
        self.plot.setMinimumSize(QtCore.QSize(0, 150))
        #self.plot.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.plot.setFrameShadow(QtGui.QFrame.Raised)
        self.plot.setObjectName(_fromUtf8("plot"))
        self.verticalLayout.addWidget(self.plot)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Panel)
        self.label.setText(QtGui.QApplication.translate("Panel", "time span [s] (0: all time)", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.t_range = QtGui.QSpinBox(Panel)
        self.t_range.setObjectName(_fromUtf8("t_range"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.t_range)
        self.label_2 = QtGui.QLabel(Panel)
        self.label_2.setText(QtGui.QApplication.translate("Panel", "integration time [ms]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.integration_time = QtGui.QSpinBox(Panel)
        self.integration_time.setObjectName(_fromUtf8("integration_time"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.integration_time)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Panel)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        pass

from chaco_plot import TimeTracePlot
