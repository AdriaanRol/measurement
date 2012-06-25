# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\qtlab_cyclops\source\gui\cyclops\panels\designer\setup_ctrl.ui'
#
# Created: Fri Jul 22 12:42:01 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName("Panel")
        Panel.resize(320, 752)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Panel.sizePolicy().hasHeightForWidth())
        Panel.setSizePolicy(sizePolicy)
        Panel.setMinimumSize(QtCore.QSize(320, 710))
        self.BlockMillennia = QtGui.QPushButton(Panel)
        self.BlockMillennia.setGeometry(QtCore.QRect(10, 10, 100, 23))
        self.BlockMillennia.setObjectName("BlockMillennia")
        self.BlockNewFocus = QtGui.QPushButton(Panel)
        self.BlockNewFocus.setGeometry(QtCore.QRect(9, 40, 100, 23))
        self.BlockNewFocus.setObjectName("BlockNewFocus")
        self.PowermeterIn = QtGui.QPushButton(Panel)
        self.PowermeterIn.setGeometry(QtCore.QRect(9, 70, 100, 23))
        self.PowermeterIn.setObjectName("PowermeterIn")
        self.DefaultSettings = QtGui.QPushButton(Panel)
        self.DefaultSettings.setGeometry(QtCore.QRect(19, 190, 191, 23))
        self.DefaultSettings.setObjectName("DefaultSettings")
        self.PowermeterOut = QtGui.QPushButton(Panel)
        self.PowermeterOut.setGeometry(QtCore.QRect(120, 70, 100, 23))
        self.PowermeterOut.setObjectName("PowermeterOut")
        self.UnblockNewFocus = QtGui.QPushButton(Panel)
        self.UnblockNewFocus.setGeometry(QtCore.QRect(120, 40, 100, 23))
        self.UnblockNewFocus.setObjectName("UnblockNewFocus")
        self.UnblockMillennia = QtGui.QPushButton(Panel)
        self.UnblockMillennia.setGeometry(QtCore.QRect(120, 10, 100, 23))
        self.UnblockMillennia.setObjectName("UnblockMillennia")
        self.FlipBeamPath = QtGui.QPushButton(Panel)
        self.FlipBeamPath.setGeometry(QtCore.QRect(60, 160, 111, 23))
        self.FlipBeamPath.setObjectName("FlipBeamPath")
        self.SetPowerGreen = QtGui.QPushButton(Panel)
        self.SetPowerGreen.setGeometry(QtCore.QRect(9, 240, 100, 23))
        self.SetPowerGreen.setObjectName("SetPowerGreen")
        self.SetPowerRed = QtGui.QPushButton(Panel)
        self.SetPowerRed.setGeometry(QtCore.QRect(9, 310, 100, 23))
        self.SetPowerRed.setObjectName("SetPowerRed")
        self.PowerRed = QtGui.QDoubleSpinBox(Panel)
        self.PowerRed.setGeometry(QtCore.QRect(120, 310, 71, 20))
        self.PowerRed.setDecimals(1)
        self.PowerRed.setMaximum(100000.0)
        self.PowerRed.setProperty("value", 100.0)
        self.PowerRed.setObjectName("PowerRed")
        self.label_2 = QtGui.QLabel(Panel)
        self.label_2.setGeometry(QtCore.QRect(200, 310, 16, 16))
        self.label_2.setObjectName("label_2")
        self.AOM_on_ADwin = QtGui.QCheckBox(Panel)
        self.AOM_on_ADwin.setGeometry(QtCore.QRect(9, 221, 177, 17))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AOM_on_ADwin.sizePolicy().hasHeightForWidth())
        self.AOM_on_ADwin.setSizePolicy(sizePolicy)
        self.AOM_on_ADwin.setChecked(True)
        self.AOM_on_ADwin.setObjectName("AOM_on_ADwin")
        self.AttocubeUp = QtGui.QPushButton(Panel)
        self.AttocubeUp.setGeometry(QtCore.QRect(9, 380, 100, 23))
        self.AttocubeUp.setObjectName("AttocubeUp")
        self.AttocubeDown = QtGui.QPushButton(Panel)
        self.AttocubeDown.setGeometry(QtCore.QRect(120, 380, 100, 23))
        self.AttocubeDown.setObjectName("AttocubeDown")
        self.label = QtGui.QLabel(Panel)
        self.label.setGeometry(QtCore.QRect(200, 240, 16, 16))
        self.label.setObjectName("label")
        self.PowerGreen = QtGui.QDoubleSpinBox(Panel)
        self.PowerGreen.setGeometry(QtCore.QRect(120, 240, 71, 20))
        self.PowerGreen.setDecimals(1)
        self.PowerGreen.setMaximum(1000.0)
        self.PowerGreen.setProperty("value", 300.0)
        self.PowerGreen.setObjectName("PowerGreen")
        self.GetPowerGreen = QtGui.QPushButton(Panel)
        self.GetPowerGreen.setGeometry(QtCore.QRect(9, 270, 100, 23))
        self.GetPowerGreen.setObjectName("GetPowerGreen")
        self.GetPowerRed = QtGui.QPushButton(Panel)
        self.GetPowerRed.setGeometry(QtCore.QRect(9, 340, 100, 23))
        self.GetPowerRed.setObjectName("GetPowerRed")
        self.CalibrateGreenAOM = QtGui.QPushButton(Panel)
        self.CalibrateGreenAOM.setGeometry(QtCore.QRect(120, 270, 100, 23))
        self.CalibrateGreenAOM.setObjectName("CalibrateGreenAOM")
        self.CalibrateRedAOM = QtGui.QPushButton(Panel)
        self.CalibrateRedAOM.setGeometry(QtCore.QRect(120, 340, 100, 23))
        self.CalibrateRedAOM.setObjectName("CalibrateRedAOM")
        self.line = QtGui.QFrame(Panel)
        self.line.setGeometry(QtCore.QRect(9, 212, 211, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtGui.QFrame(Panel)
        self.line_2.setGeometry(QtCore.QRect(9, 290, 211, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtGui.QFrame(Panel)
        self.line_3.setGeometry(QtCore.QRect(9, 360, 211, 16))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.PiezoChannel = QtGui.QSpinBox(Panel)
        self.PiezoChannel.setGeometry(QtCore.QRect(120, 568, 70, 20))
        self.PiezoChannel.setMinimum(1)
        self.PiezoChannel.setMaximum(4)
        self.PiezoChannel.setObjectName("PiezoChannel")
        self.PiezoSteps = QtGui.QSpinBox(Panel)
        self.PiezoSteps.setGeometry(QtCore.QRect(120, 620, 70, 20))
        self.PiezoSteps.setMinimum(1)
        self.PiezoSteps.setProperty("value", 1)
        self.PiezoSteps.setObjectName("PiezoSteps")
        self.label_3 = QtGui.QLabel(Panel)
        self.label_3.setGeometry(QtCore.QRect(20, 568, 39, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(Panel)
        self.label_4.setGeometry(QtCore.QRect(20, 620, 27, 16))
        self.label_4.setObjectName("label_4")
        self.PiezoMirrorMax = QtGui.QPushButton(Panel)
        self.PiezoMirrorMax.setGeometry(QtCore.QRect(60, 656, 100, 23))
        self.PiezoMirrorMax.setObjectName("PiezoMirrorMax")
        self.BlockChA = QtGui.QPushButton(Panel)
        self.BlockChA.setGeometry(QtCore.QRect(9, 100, 100, 23))
        self.BlockChA.setObjectName("BlockChA")
        self.UnblockChA = QtGui.QPushButton(Panel)
        self.UnblockChA.setGeometry(QtCore.QRect(120, 100, 100, 23))
        self.UnblockChA.setObjectName("UnblockChA")
        self.BlockChB = QtGui.QPushButton(Panel)
        self.BlockChB.setGeometry(QtCore.QRect(9, 130, 100, 23))
        self.BlockChB.setObjectName("BlockChB")
        self.UnblockChB = QtGui.QPushButton(Panel)
        self.UnblockChB.setGeometry(QtCore.QRect(120, 130, 100, 23))
        self.UnblockChB.setObjectName("UnblockChB")
        self.line_4 = QtGui.QFrame(Panel)
        self.line_4.setGeometry(QtCore.QRect(9, 496, 199, 16))
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.PiezoAxis = QtGui.QSpinBox(Panel)
        self.PiezoAxis.setGeometry(QtCore.QRect(120, 594, 70, 20))
        self.PiezoAxis.setMinimum(1)
        self.PiezoAxis.setMaximum(2)
        self.PiezoAxis.setObjectName("PiezoAxis")
        self.label_5 = QtGui.QLabel(Panel)
        self.label_5.setGeometry(QtCore.QRect(20, 594, 20, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtGui.QLabel(Panel)
        self.label_6.setGeometry(QtCore.QRect(20, 542, 47, 16))
        self.label_6.setObjectName("label_6")
        self.PiezoController = QtGui.QSpinBox(Panel)
        self.PiezoController.setGeometry(QtCore.QRect(120, 542, 70, 20))
        self.PiezoController.setMinimum(1)
        self.PiezoController.setMaximum(2)
        self.PiezoController.setObjectName("PiezoController")
        self.PiezoMirrorMinus = QtGui.QPushButton(Panel)
        self.PiezoMirrorMinus.setGeometry(QtCore.QRect(9, 513, 100, 23))
        self.PiezoMirrorMinus.setObjectName("PiezoMirrorMinus")
        self.PiezoMirrorPlus = QtGui.QPushButton(Panel)
        self.PiezoMirrorPlus.setGeometry(QtCore.QRect(120, 513, 100, 23))
        self.PiezoMirrorPlus.setObjectName("PiezoMirrorPlus")
        self.line_5 = QtGui.QFrame(Panel)
        self.line_5.setGeometry(QtCore.QRect(9, 400, 211, 16))
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.OptimizeXY = QtGui.QPushButton(Panel)
        self.OptimizeXY.setGeometry(QtCore.QRect(9, 440, 100, 23))
        self.OptimizeXY.setObjectName("OptimizeXY")
        self.OptimizeZ = QtGui.QPushButton(Panel)
        self.OptimizeZ.setGeometry(QtCore.QRect(120, 440, 100, 23))
        self.OptimizeZ.setObjectName("OptimizeZ")
        self.LT_settings = QtGui.QCheckBox(Panel)
        self.LT_settings.setGeometry(QtCore.QRect(130, 420, 74, 17))
        self.LT_settings.setObjectName("LT_settings")
        self.label_7 = QtGui.QLabel(Panel)
        self.label_7.setGeometry(QtCore.QRect(20, 416, 39, 16))
        self.label_7.setObjectName("label_7")
        self.GetTemperatureA = QtGui.QPushButton(Panel)
        self.GetTemperatureA.setGeometry(QtCore.QRect(9, 684, 100, 23))
        self.GetTemperatureA.setObjectName("GetTemperatureA")
        self.GetTemperatureB = QtGui.QPushButton(Panel)
        self.GetTemperatureB.setGeometry(QtCore.QRect(9, 713, 100, 23))
        self.GetTemperatureB.setObjectName("GetTemperatureB")
        self.TemperatureA = QtGui.QDoubleSpinBox(Panel)
        self.TemperatureA.setGeometry(QtCore.QRect(120, 685, 70, 20))
        self.TemperatureA.setMaximum(500.0)
        self.TemperatureA.setObjectName("TemperatureA")
        self.TemperatureB = QtGui.QDoubleSpinBox(Panel)
        self.TemperatureB.setGeometry(QtCore.QRect(120, 714, 70, 20))
        self.TemperatureB.setMaximum(500.0)
        self.TemperatureB.setObjectName("TemperatureB")
        self.line_6 = QtGui.QFrame(Panel)
        self.line_6.setGeometry(QtCore.QRect(9, 675, 199, 16))
        self.line_6.setFrameShape(QtGui.QFrame.HLine)
        self.line_6.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.label_8 = QtGui.QLabel(Panel)
        self.label_8.setGeometry(QtCore.QRect(200, 684, 16, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtGui.QLabel(Panel)
        self.label_9.setGeometry(QtCore.QRect(200, 713, 16, 16))
        self.label_9.setObjectName("label_9")
        self.z_Position_Slider = QtGui.QSlider(Panel)
        self.z_Position_Slider.setGeometry(QtCore.QRect(270, 40, 21, 661))
        self.z_Position_Slider.setMaximum(1000)
        self.z_Position_Slider.setProperty("value", 500)
        self.z_Position_Slider.setOrientation(QtCore.Qt.Vertical)
        self.z_Position_Slider.setObjectName("z_Position_Slider")
        self.z_Position = QtGui.QDoubleSpinBox(Panel)
        self.z_Position.setEnabled(False)
        self.z_Position.setGeometry(QtCore.QRect(250, 710, 62, 22))
        self.z_Position.setMaximum(24.0)
        self.z_Position.setObjectName("z_Position")
        self.line_7 = QtGui.QFrame(Panel)
        self.line_7.setGeometry(QtCore.QRect(220, 10, 20, 721))
        self.line_7.setFrameShape(QtGui.QFrame.VLine)
        self.line_7.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.label_10 = QtGui.QLabel(Panel)
        self.label_10.setGeometry(QtCore.QRect(240, 10, 81, 16))
        self.label_10.setObjectName("label_10")
        self.OptimizeChannel = QtGui.QSpinBox(Panel)
        self.OptimizeChannel.setGeometry(QtCore.QRect(120, 470, 70, 20))
        self.OptimizeChannel.setMinimum(1)
        self.OptimizeChannel.setMaximum(5)
        self.OptimizeChannel.setProperty("value", 5)
        self.OptimizeChannel.setObjectName("OptimizeChannel")
        self.label_11 = QtGui.QLabel(Panel)
        self.label_11.setGeometry(QtCore.QRect(20, 470, 91, 16))
        self.label_11.setObjectName("label_11")

        self.retranslateUi(Panel)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.BlockMillennia.setText(QtGui.QApplication.translate("Panel", "block Millennia", None, QtGui.QApplication.UnicodeUTF8))
        self.BlockNewFocus.setText(QtGui.QApplication.translate("Panel", "block NewFocus", None, QtGui.QApplication.UnicodeUTF8))
        self.PowermeterIn.setText(QtGui.QApplication.translate("Panel", "Powermeter in", None, QtGui.QApplication.UnicodeUTF8))
        self.DefaultSettings.setText(QtGui.QApplication.translate("Panel", "default settings", None, QtGui.QApplication.UnicodeUTF8))
        self.PowermeterOut.setText(QtGui.QApplication.translate("Panel", "Powermeter out", None, QtGui.QApplication.UnicodeUTF8))
        self.UnblockNewFocus.setText(QtGui.QApplication.translate("Panel", "unblock NewFocus", None, QtGui.QApplication.UnicodeUTF8))
        self.UnblockMillennia.setText(QtGui.QApplication.translate("Panel", "unblock Millennia", None, QtGui.QApplication.UnicodeUTF8))
        self.FlipBeamPath.setText(QtGui.QApplication.translate("Panel", "flip beam path", None, QtGui.QApplication.UnicodeUTF8))
        self.SetPowerGreen.setText(QtGui.QApplication.translate("Panel", "set green power", None, QtGui.QApplication.UnicodeUTF8))
        self.SetPowerRed.setText(QtGui.QApplication.translate("Panel", "set red power", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Panel", "nW", None, QtGui.QApplication.UnicodeUTF8))
        self.AOM_on_ADwin.setText(QtGui.QApplication.translate("Panel", "ADwin controls green laser AOM", None, QtGui.QApplication.UnicodeUTF8))
        self.AttocubeUp.setText(QtGui.QApplication.translate("Panel", "Attocube up", None, QtGui.QApplication.UnicodeUTF8))
        self.AttocubeDown.setText(QtGui.QApplication.translate("Panel", "Attocube down", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Panel", "µW", None, QtGui.QApplication.UnicodeUTF8))
        self.GetPowerGreen.setText(QtGui.QApplication.translate("Panel", "get green power", None, QtGui.QApplication.UnicodeUTF8))
        self.GetPowerRed.setText(QtGui.QApplication.translate("Panel", "get red power", None, QtGui.QApplication.UnicodeUTF8))
        self.CalibrateGreenAOM.setText(QtGui.QApplication.translate("Panel", "calibrate gr. AOM", None, QtGui.QApplication.UnicodeUTF8))
        self.CalibrateRedAOM.setText(QtGui.QApplication.translate("Panel", "calibrate red AOM", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Panel", "Channel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Panel", "Steps", None, QtGui.QApplication.UnicodeUTF8))
        self.PiezoMirrorMax.setText(QtGui.QApplication.translate("Panel", "find maximum", None, QtGui.QApplication.UnicodeUTF8))
        self.BlockChA.setText(QtGui.QApplication.translate("Panel", "block channel A", None, QtGui.QApplication.UnicodeUTF8))
        self.UnblockChA.setText(QtGui.QApplication.translate("Panel", "unblock channel A", None, QtGui.QApplication.UnicodeUTF8))
        self.BlockChB.setText(QtGui.QApplication.translate("Panel", "block channel B", None, QtGui.QApplication.UnicodeUTF8))
        self.UnblockChB.setText(QtGui.QApplication.translate("Panel", "unblock channel B", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Panel", "Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Panel", "Controller", None, QtGui.QApplication.UnicodeUTF8))
        self.PiezoMirrorMinus.setText(QtGui.QApplication.translate("Panel", "Piezo Mirror -", None, QtGui.QApplication.UnicodeUTF8))
        self.PiezoMirrorPlus.setText(QtGui.QApplication.translate("Panel", "Piezo Mirror +", None, QtGui.QApplication.UnicodeUTF8))
        self.OptimizeXY.setText(QtGui.QApplication.translate("Panel", "Optimize XY", None, QtGui.QApplication.UnicodeUTF8))
        self.OptimizeZ.setText(QtGui.QApplication.translate("Panel", "Optimize Z", None, QtGui.QApplication.UnicodeUTF8))
        self.LT_settings.setText(QtGui.QApplication.translate("Panel", "LT settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Panel", "Scanner", None, QtGui.QApplication.UnicodeUTF8))
        self.GetTemperatureA.setText(QtGui.QApplication.translate("Panel", "get temperature A", None, QtGui.QApplication.UnicodeUTF8))
        self.GetTemperatureB.setText(QtGui.QApplication.translate("Panel", "get temperature B", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Panel", "K", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Panel", "K", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Panel", "z-axis scanner", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Panel", "Optimize Channel", None, QtGui.QApplication.UnicodeUTF8))
