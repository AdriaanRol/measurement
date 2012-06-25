# this panel controls parameters of the optical setup, 
# such as beam paths, laser power, and alignment
#
# Author: Lucio Robledo <l.m.robledoesparza@tudelft.nl>

import numpy

from panel import Panel
from ui_setup_ctrl import Ui_Panel

from PyQt4 import QtCore
from PyQt4.Qwt5.Qwt import QwtPlot as Qwt

class SetupPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui  
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        self.ui.AOM_on_ADwin.setChecked(self._ins.get_AOMonADwin())
        self.ui.LT_settings.setChecked(self._ins.get_LT_settings())
        self.ui.TemperatureA.setValue(self._ins.get_TemperatureA())
        self.ui.TemperatureB.setValue(self._ins.get_TemperatureB())
        self.ui.z_Position.setValue(self._ins.get_z_Position())
        if self._ins.get_LT_settings() == 0:
            self.ui.z_Position_Slider.setValue(self.ui.z_Position.value()*1000/24)
        else:
            self.ui.z_Position_Slider.setValue(self.ui.z_Position.value()*1000/15)
        
        self.ui.BlockMillennia.clicked.connect(self.BlockMillennia)
        self.ui.UnblockMillennia.clicked.connect(self.UnblockMillennia)
        self.ui.BlockChA.clicked.connect(self.BlockChA)
        self.ui.UnblockChA.clicked.connect(self.UnblockChA)
        self.ui.BlockChB.clicked.connect(self.BlockChB)
        self.ui.UnblockChB.clicked.connect(self.UnblockChB)
        self.ui.BlockNewFocus.clicked.connect(self.BlockNewFocus)
        self.ui.UnblockNewFocus.clicked.connect(self.UnblockNewFocus)
        self.ui.PowermeterIn.clicked.connect(self.PowermeterIn)
        self.ui.PowermeterOut.clicked.connect(self.PowermeterOut)
        self.ui.FlipBeamPath.clicked.connect(self.FlipBeamPath)
        self.ui.DefaultSettings.clicked.connect(self.DefaultSettings)
        self.ui.SetPowerGreen.clicked.connect(self.SetPowerGreen)
        self.ui.GetPowerGreen.clicked.connect(self.GetPowerGreen)
        self.ui.CalibrateGreenAOM.clicked.connect(self.CalibrateGreenAOM)
        self.ui.SetPowerRed.clicked.connect(self.SetPowerRed)
        self.ui.GetPowerRed.clicked.connect(self.GetPowerRed)
        self.ui.CalibrateRedAOM.clicked.connect(self.CalibrateRedAOM)
        self.ui.AttocubeUp.clicked.connect(self.AttocubeUp)
        self.ui.AttocubeDown.clicked.connect(self.AttocubeDown)
        self.ui.PiezoMirrorPlus.clicked.connect(self.PiezoMirrorPlus)
        self.ui.PiezoMirrorMinus.clicked.connect(self.PiezoMirrorMinus)
        self.ui.PiezoMirrorMax.clicked.connect(self.PiezoMirrorMax)
        self.ui.AOM_on_ADwin.stateChanged.connect(self.AOM_on_ADwin_Changed)
        self.ui.LT_settings.stateChanged.connect(self.LT_settings_Changed)
        self.ui.OptimizeXY.clicked.connect(self.OptimizeXY)
        self.ui.OptimizeZ.clicked.connect(self.OptimizeZ)
        self.ui.z_Position_Slider.valueChanged.connect(self.z_Position_Changed)
        self.ui.GetTemperatureA.clicked.connect(self.GetTemperatureA)
        self.ui.GetTemperatureB.clicked.connect(self.GetTemperatureB)


    # this method automatically gets called when instrument parameters take
    # a new value, i.e. any get_* or set_* function of the instrument has been
    # called. 

    def _instrument_changed(self, changes):

        # this means that the instrument has just been set on, meaning that
        # we need to reset the local data cache
        if changes.has_key('is_running'):
            self._reset(bool(changes['is_running']))

        if changes.has_key('z_Position'):
            self.ui.z_Position.setValue(changes['z_Position'])
            if self._ins.get_LT_settings() == 0:
                self.ui.z_Position_Slider.setValue(self.ui.z_Position.value()*1000/24)
            else:
                self.ui.z_Position_Slider.setValue(self.ui.z_Position.value()*1000/15)

        if changes.has_key('TemperatureA'):
            self.ui.TemperatureA.setValue(changes['TemperatureA'])

        if changes.has_key('TemperatureB'):
            self.ui.TemperatureB.setValue(changes['TemperatureB'])

        if changes.has_key('PowerRed'):
            self.ui.PowerRed.setValue(changes['PowerRed']*1e9)

        if changes.has_key('PowerGreen'):
            self.ui.PowerGreen.setValue(changes['PowerGreen']*1e6)

        if changes.has_key('AOMonADwin'):
            self.ui.AOM_on_ADwin.setChecked(changes['AOMonADwin'])

        if changes.has_key('LT_settings'):
            self.ui.LT_settings.setChecked(changes['LT_settings'])

    @QtCore.pyqtSlot(int)
    def z_Position_Changed(self, val):
        if self._ins.get_LT_settings() == 0:
            self._ins.set_z_Position(float(val)/1000.0*24.0)
        else:
            self._ins.set_z_Position(float(val)/1000.0*15.0)

    @QtCore.pyqtSlot(bool)
    def GetTemperatureB(self, bool):
        self._ins.get_TemperatureB()

    @QtCore.pyqtSlot(bool)
    def GetTemperatureA(self, bool):
        self._ins.get_TemperatureA()

    @QtCore.pyqtSlot(bool)
    def BlockMillennia(self, bool):
        self._ins.Millennia_Laser_Block()

    @QtCore.pyqtSlot(bool)
    def UnblockMillennia(self, bool):
        self._ins.Millennia_Laser_Unblock()

    @QtCore.pyqtSlot(bool)
    def BlockNewFocus(self, bool):
        self._ins.Newfocus_Laser_Block()

    @QtCore.pyqtSlot(bool)
    def UnblockNewFocus(self, bool):
        self._ins.Newfocus_Laser_Unblock()

    @QtCore.pyqtSlot(bool)
    def BlockChA(self, bool):
        self._ins.Channel_A_Block()

    @QtCore.pyqtSlot(bool)
    def UnblockChA(self, bool):
        self._ins.Channel_A_Unblock()

    @QtCore.pyqtSlot(bool)
    def BlockChB(self, bool):
        self._ins.Channel_B_Block()

    @QtCore.pyqtSlot(bool)
    def UnblockChB(self, bool):
        self._ins.Channel_B_Unblock()

    @QtCore.pyqtSlot(bool)
    def PowermeterIn(self, bool):
        self._ins.Powermeter_In()

    @QtCore.pyqtSlot(bool)
    def PowermeterOut(self, bool):
        self._ins.Powermeter_Out()

    @QtCore.pyqtSlot(bool)
    def FlipBeamPath(self, bool):
        self._ins.SwitchDichroic()

    @QtCore.pyqtSlot(bool)
    def DefaultSettings(self, bool):
        self._ins.Default_Settings()

    @QtCore.pyqtSlot(bool)
    def AttocubeUp(self, bool):
        self._ins.Attocube_Up()

    @QtCore.pyqtSlot(bool)
    def AttocubeDown(self, bool):
        self._ins.Attocube_Down()

    @QtCore.pyqtSlot(bool)
    def GetPowerGreen(self, bool):
        self._ins.get_PowerGreen()

    @QtCore.pyqtSlot(bool)
    def GetPowerRed(self, bool):
        self._ins.get_PowerRed()

    @QtCore.pyqtSlot(bool)
    def SetPowerGreen(self, bool):
        self._ins.set_PowerGreen(self.ui.PowerGreen.value()*1e-6)

    @QtCore.pyqtSlot(bool)
    def SetPowerRed(self, bool):
        self._ins.set_PowerRed(self.ui.PowerRed.value()*1e-9)

    @QtCore.pyqtSlot(int)
    def AOM_on_ADwin_Changed(self, val):
        if val > 0:
            self._ins.set_AOMonADwin(True)
        else:
            self._ins.set_AOMonADwin(False)
          
    @QtCore.pyqtSlot(int)
    def LT_settings_Changed(self, val):
        if val > 0:
            self._ins.set_LT_settings(1)
        else:
            self._ins.set_LT_settings(0)
          
    @QtCore.pyqtSlot(bool)
    def CalibrateGreenAOM(self, bool):
#        self._ins.SimpleCalibrateGreenAOM()
        if (self.ui.AOM_on_ADwin.checkState() > 0):
            self._ins.CalibrateGreenAOM(V_max = 8.0)
        else:
            self._ins.CalibrateGreenAOM(V_max = 1.0)

    @QtCore.pyqtSlot(bool)
    def CalibrateRedAOM(self, bool):
#        self._ins.SimpleCalibrateRedAOM()
        self._ins.CalibrateRedAOM(V_max = 1.0)

    @QtCore.pyqtSlot(bool)
    def OptimizeXY(self, bool):
        self._ins.OptimizeXY(counter = self.ui.OptimizeChannel.value())

    def OptimizeZ(self, bool):
        self._ins.OptimizeZ(counter = self.ui.OptimizeChannel.value())

    @QtCore.pyqtSlot(bool)
    def PiezoMirrorPlus(self, bool):
        self._ins.Piezo_Mirror_Plus(self.ui.PiezoController.value(),self.ui.PiezoChannel.value(),self.ui.PiezoAxis.value(),self.ui.PiezoSteps.value())

    @QtCore.pyqtSlot(bool)
    def PiezoMirrorMinus(self, bool):
        self._ins.Piezo_Mirror_Minus(self.ui.PiezoController.value(),self.ui.PiezoChannel.value(),self.ui.PiezoAxis.value(),self.ui.PiezoSteps.value())

    @QtCore.pyqtSlot(bool)
    def PiezoMirrorMax(self, bool):
        self._ins.PiezoFindMax(PiezoController = self.ui.PiezoController.value(), PiezoChannel = self.ui.PiezoChannel.value(), PiezoAxis = self.ui.PiezoAxis.value())


