# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'whackyscan.ui'
#
# Created: Thu Aug 04 23:36:00 2011
#      by: PyQt4 UI code generator 4.8.4
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
        Panel.resize(512, 287)
        self.gridLayout = QtGui.QGridLayout(Panel)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.xcut_plot = LinePlot(Panel)
        self.xcut_plot.setObjectName(_fromUtf8("xcut_plot"))
        self.gridLayout.addWidget(self.xcut_plot, 0, 0, 2, 4)
        self.xycut_plot = ColorPlot(Panel)
        self.xycut_plot.setObjectName(_fromUtf8("xycut_plot"))
        self.gridLayout.addWidget(self.xycut_plot, 0, 4, 2, 4)
        self.current_z = QtGui.QSlider(Panel)
        self.current_z.setOrientation(QtCore.Qt.Vertical)
        self.current_z.setObjectName(_fromUtf8("current_z"))
        self.gridLayout.addWidget(self.current_z, 0, 8, 1, 1)
        self.label_4 = QtGui.QLabel(Panel)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 8, 1, 1)
        self.label = QtGui.QLabel(Panel)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.cube_size = QtGui.QDoubleSpinBox(Panel)
        self.cube_size.setMinimum(1.0)
        self.cube_size.setProperty(_fromUtf8("value"), 4.0)
        self.cube_size.setObjectName(_fromUtf8("cube_size"))
        self.gridLayout.addWidget(self.cube_size, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Panel)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 2, 1, 1)
        self.pxperdim = QtGui.QSpinBox(Panel)
        self.pxperdim.setMinimum(3)
        self.pxperdim.setProperty(_fromUtf8("value"), 11)
        self.pxperdim.setObjectName(_fromUtf8("pxperdim"))
        self.gridLayout.addWidget(self.pxperdim, 2, 3, 1, 1)
        self.label_2 = QtGui.QLabel(Panel)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 4, 1, 1)
        self.pxtime = QtGui.QSpinBox(Panel)
        self.pxtime.setMinimum(1)
        self.pxtime.setObjectName(_fromUtf8("pxtime"))
        self.gridLayout.addWidget(self.pxtime, 2, 5, 1, 1)
        self.go = QtGui.QPushButton(Panel)
        self.go.setObjectName(_fromUtf8("go"))
        self.gridLayout.addWidget(self.go, 2, 6, 1, 1)
        self.stop = QtGui.QPushButton(Panel)
        self.stop.setObjectName(_fromUtf8("stop"))
        self.gridLayout.addWidget(self.stop, 2, 7, 1, 2)

        self.retranslateUi(Panel)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Panel", "z", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Panel", "Cube size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Panel", "px / dimension", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Panel", "pxtime [ms]", None, QtGui.QApplication.UnicodeUTF8))
        self.go.setText(QtGui.QApplication.translate("Panel", "Go", None, QtGui.QApplication.UnicodeUTF8))
        self.stop.setText(QtGui.QApplication.translate("Panel", "Stop", None, QtGui.QApplication.UnicodeUTF8))

from chaco_plot import ColorPlot, LinePlot
