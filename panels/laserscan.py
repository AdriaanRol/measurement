# a 2d scan panel
#
# An example of a 2d scanner that scans an area line by line.
# if the instrument is running, the panel gets notified that new
# data is available and gets it from the instrument and caches is
# locally. since this costs cpu runtime, the 2d scan plot is not
# updated on demand, but slower, triggered by the panel timer.
#
# Author: Wolfgang Pfaff <w.pfaff@tudelft.nl>
import numpy
import time

from panel import Panel
from ui_laserscan import Ui_Panel

from PyQt4 import QtCore
from PyQt4.Qwt5.Qwt import QwtPlot as Qwt

class LaserscanPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui  
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        # setting up the basic plot properties
        # the name is not absolutely required, but gives
        # the plot toolbar a name
#        self.ui.chart_frequency.set_name('Single laser scan')
        self.ui.plot_2D.set_axis_label(Qwt.xBottom, 'scan number')
        self.ui.plot_2D.set_axis_label(Qwt.yLeft, 'scan step')

        self.ui.chart_frequency.set_name('Wavemeter')
        self.ui.chart_frequency.set_axis_label(Qwt.xBottom, 'Time')
        self.ui.chart_frequency.set_axis_label(Qwt.yLeft, 'Rel. laser frequency [GHz]')

#        self.ui.trace_frequency.set_name('Frequency single scan')
        self.ui.trace_frequency.set_axis_label(Qwt.xBottom, 'scan step')
        self.ui.trace_frequency.set_axis_label(Qwt.yLeft, 'frequency [GHz]')

#        self.ui.trace_counts.set_name('Counts single scan')
        self.ui.trace_counts.set_axis_label(Qwt.xBottom, 'scan step')
        self.ui.trace_counts.set_axis_label(Qwt.yLeft, 'counts')


        self.ui.chart_frequency.set_t_range(10)
#        self.ui.chart_frequency.set_axis_scale(Qwt.yLeft,470400,470600,0)

        # enable the cross hair positioning
        # FIXME: also set the crosshair via signal to reflect changes from
        # outside
        # self.ui.plot._init_crosshair()
        # self.ui.plot.crosshair_set.connect(self._ins.move_abs_xy)
        

        # read the instrument parameters and set the input
        # fields accordingly
        self.ui.StartVoltage.setValue(self._ins.get_StartVoltage())
        self.ui.StepVoltage.setValue(self._ins.get_StepVoltage())
        self.ui.ScanSteps.setValue(self._ins.get_ScanSteps())
        self.ui.ScanCount.setValue(self._ins.get_ScanCount())
        self.ui.InitialWait.setValue(self._ins.get_InitialWait())
        self.ui.IntegrationTime.setValue(self._ins.get_IntegrationTime())
        self.ui.LaserInitialize.setChecked(self._ins.get_LaserInitialize())
        self.ui.ScanBack.setChecked(self._ins.get_ScanBack())
        self.ui.ScanBackTime.setValue(self._ins.get_ScanBackTime())
        self.ui.DCStarkShiftSweep.setChecked(self._ins.get_DCStarkShiftSweep())
        self.ui.GateSweep.setChecked(self._ins.get_GateSweep())
        self.ui.ModulateGate.setChecked(self._ins.get_ModulateGate())

        enabled_state = not(self.ui.GateSweep.checkState())
        self.ui.StartVoltage.setEnabled(enabled_state)
        self.ui.StepVoltage.setEnabled(enabled_state)
        self.ui.LaserInitialize.setEnabled(enabled_state)
        self.ui.ScanBack.setEnabled(enabled_state)
        self.ui.ScanSteps.setEnabled(enabled_state)
        self.ui.ScanBackTime.setEnabled(enabled_state)
        self.ui.ModulateGate.setEnabled(not(enabled_state))
        self.ui.DCStarkShiftSweep.setEnabled(enabled_state)

        self.ui.DCStart.setValue(self._ins.get_DCStart())
        self.ui.DCStop.setValue(self._ins.get_DCStop())
        self.ui.DCstepsize.setValue(self._ins.get_DCstepsize())
        self.ui.PulseAOM.setChecked(self._ins.get_PulseAOM())
        self.ui.PulseDuration.setValue(self._ins.get_PulseDuration())
        self.ui.PowerLevelPulse.setValue(self._ins.get_PowerLevelPulse())
        self.ui.PowerLevelScan.setValue(self._ins.get_PowerLevelScan())
        self.ui.PowerLevelOn.setValue(self._ins.get_PowerLevelOn())
        self.ui.WavemeterChannel.setValue(self._ins.get_WavemeterChannel())
        self.ui.CounterChannel.setValue(self._ins.get_CounterChannel())
        self.ui.FrequencyAveraging.setValue(self._ins.get_FrequencyAveraging())
        self.ui.FrequencyInterpolationStep.setValue(self._ins.get_FrequencyInterpolationStep())
        self.ui.FrequencyReference.setValue(self._ins.get_FrequencyReference())
        self.ui.ModeHopThreshold.setValue(self._ins.get_ModeHopThreshold())
        self.ui.LaserOn.setChecked(self._ins.get_LaserOn())
        self.ui.AutoOptimizeXY.setChecked(self._ins.get_AutoOptimizeXY())
        self.ui.AutoOptimizeZ.setChecked(self._ins.get_AutoOptimizeZ())
        self.ui.OptimizeInterval.setValue(self._ins.get_OptimizeInterval())
        self.ui.CurrentScan.setValue(self._ins.get_ScanIndex())
        self.ui.MWOn.setChecked(self._ins.get_MWOn())
        self.ui.MWfrequency.setValue(self._ins.get_MWfrequency()/1e9)
        self.ui.MWpower.setValue(self._ins.get_MWpower())
        self.ui.DCGate.setValue(self._ins.get_DCGate())
        self.ui.CurrentFrequency.setValue(self._ins.get_CurrentFrequency())
        self.ui.ScanVoltage.setValue(self._ins.get_ScanVoltage())
        self.ui.PiezoVoltage.setValue(self._ins.get_PiezoVoltage())
        self.ui.Gate1Voltage.setValue(self._ins.get_Gate1Voltage())
        self.ui.Gate2Voltage.setValue(self._ins.get_Gate2Voltage())
        self.ui.LockFrequency.setChecked(self._ins.get_LockFrequency())

        enabled_state = self.ui.LockFrequency.checkState()
        self.ui.FrequencyStep.setEnabled(enabled_state)
        self.ui.StepUp.setEnabled(enabled_state)
        self.ui.StepDown.setEnabled(enabled_state)

        enabled_state = self.ui.MWOn.checkState()
        self.ui.MWfrequency.setEnabled(enabled_state)
        self.ui.MWpower.setEnabled(enabled_state)
        self.ui.SetMWfrequency.setEnabled(enabled_state)
        self.ui.SetMWpower.setEnabled(enabled_state)

        enabled_state = self.ui.ScanBack.checkState()
        self.ui.ScanBackTime.setEnabled(enabled_state)

        enabled_state = self.ui.LaserOn.checkState()
        self.ui.PiezoVoltage.setEnabled(enabled_state)
        self.ui.ScanVoltage.setEnabled(enabled_state)
        self.ui.SetPiezoVoltage.setEnabled(enabled_state)
        self.ui.SetScanVoltage.setEnabled(enabled_state)

        self.ui.LockFrequencyDeviation.setValue(self._ins.get_LockFrequencyDeviation())
        self.ui.FrequencySetpoint.setValue(self._ins.get_FrequencySetpoint() - self._ins.get_FrequencyReference())
        self.ui.FrequencyStep.setValue(self._ins.get_FrequencyStep())

        self.ui.XYScanIndex.setMinimum(0)
        self.ui.XYScanIndex.setMaximum(0)

        self.ui.StartVoltage.valueChanged.connect(self.StartVoltageChanged)
        self.ui.StepVoltage.valueChanged.connect(self.StepVoltageChanged)
        self.ui.ScanSteps.valueChanged.connect(self.ScanStepsChanged)
        self.ui.ScanCount.valueChanged.connect(self.ScanCountChanged)
        self.ui.InitialWait.valueChanged.connect(self.InitialWaitChanged)
        self.ui.IntegrationTime.valueChanged.connect(self.IntegrationTimeChanged)
        self.ui.LaserInitialize.stateChanged.connect(self.LaserInitializeChanged)
        self.ui.ScanBack.stateChanged.connect(self.ScanBackChanged)
        self.ui.ScanBackTime.valueChanged.connect(self.ScanBackTimeChanged)
        self.ui.DCStarkShiftSweep.stateChanged.connect(self.DCStarkShiftSweepChanged)
        self.ui.GateSweep.stateChanged.connect(self.GateSweepChanged)
        self.ui.ModulateGate.stateChanged.connect(self.ModulateGateChanged)
        self.ui.DCStart.valueChanged.connect(self.DCStartChanged)
        self.ui.DCStop.valueChanged.connect(self.DCStopChanged)
        self.ui.DCstepsize.valueChanged.connect(self.DCstepsizeChanged)
        self.ui.PulseAOM.stateChanged.connect(self.PulseAOMChanged)
        self.ui.PulseDuration.valueChanged.connect(self.PulseDurationChanged)
        self.ui.PowerLevelPulse.valueChanged.connect(self.PowerLevelPulseChanged)
        self.ui.PowerLevelScan.valueChanged.connect(self.PowerLevelScanChanged)
        self.ui.WavemeterChannel.valueChanged.connect(self.WavemeterChannelChanged)
        self.ui.CounterChannel.valueChanged.connect(self.CounterChannelChanged)
        self.ui.FrequencyAveraging.valueChanged.connect(self.FrequencyAveragingChanged)
        self.ui.FrequencyInterpolationStep.valueChanged.connect(self.FrequencyInterpolationStepChanged)
        self.ui.FrequencyReference.valueChanged.connect(self.FrequencyReferenceChanged)
        self.ui.ModeHopThreshold.valueChanged.connect(self.ModeHopThresholdChanged)
        self.ui.LaserOn.stateChanged.connect(self.LaserOnChanged)
        self.ui.DCGate.valueChanged.connect(self.DCGateChanged)
        self.ui.SetScanVoltage.clicked.connect(self.SetScanVoltage)
        self.ui.SetPiezoVoltage.clicked.connect(self.SetPiezoVoltage)
        self.ui.SetGate1Voltage.clicked.connect(self.SetGate1Voltage)
        self.ui.SetGate2Voltage.clicked.connect(self.SetGate2Voltage)
        self.ui.LockFrequency.stateChanged.connect(self.LockFrequencyChanged)
        self.ui.FrequencySetpoint.valueChanged.connect(self.FrequencySetpointChanged)
        self.ui.SetScanRangeCenter.clicked.connect(self.SetScanRangeCenter)
        self.ui.FrequencyStep.valueChanged.connect(self.FrequencyStepChanged)
        self.ui.StepUp.clicked.connect(self.StepUp)
        self.ui.StepDown.clicked.connect(self.StepDown)
        self.ui.StartScan.clicked.connect(self.StartScan)
        self.ui.PauseScan.clicked.connect(self.PauseScan)
        self.ui.AbortScan.clicked.connect(self.AbortScan)

        self.ui.MWOn.stateChanged.connect(self.MWOnChanged)
        self.ui.AutoOptimizeXY.stateChanged.connect(self.AutoOptimizeXYChanged)
        self.ui.AutoOptimizeZ.stateChanged.connect(self.AutoOptimizeZChanged)
        self.ui.PowerLevelOn.valueChanged.connect(self.PowerLevelOnChanged)
        self.ui.OptimizeInterval.valueChanged.connect(self.OptimizeIntervalChanged)

        self.ui.SetMWfrequency.clicked.connect(self.SetMWfrequency)
        self.ui.SetMWpower.clicked.connect(self.SetMWpower)
        self.ui.PulseAOM_manual.clicked.connect(self.PulseAOM_manual)
        self.ui.SkipToNext.clicked.connect(self.SkipToNext)

        self.ui.XYScanIndex.valueChanged.connect(self.XYScanIndexChanged)
        self.ui.Comments.textChanged.connect(self.CommentsChanged)

        self._stepping = False

        self._CurrentTraceIndex = 0
        self._CurrentScanIndex = 0
        self._new_index = 0
        self._blocked = 0
        self._trace_finished = -1

    @QtCore.pyqtSlot(bool)
    def SetScanRangeCenter(self, bool):
        self._ins.set_ScanRangeCenter(self.ui.ScanRangeCenter.value())

    @QtCore.pyqtSlot(bool)
    def SetMWfrequency(self, bool):
        self._ins.set_MWfrequency(self.ui.MWfrequency.value()*1e9)

    @QtCore.pyqtSlot(bool)
    def SetMWpower(self, bool):
        self._ins.set_MWpower(self.ui.MWpower.value())

    @QtCore.pyqtSlot(int)
    def MWOnChanged(self, val):
        self._ins.set_MWOn(val)
        enabled_state = self.ui.MWOn.checkState()
        self.ui.MWfrequency.setEnabled(enabled_state)
        self.ui.MWpower.setEnabled(enabled_state)
        self.ui.SetMWfrequency.setEnabled(enabled_state)
        self.ui.SetMWpower.setEnabled(enabled_state)

    @QtCore.pyqtSlot(int)
    def AutoOptimizeXYChanged(self, val):
        self._ins.set_AutoOptimizeXY(val)

    @QtCore.pyqtSlot(int)
    def AutoOptimizeZChanged(self, val):
        self._ins.set_AutoOptimizeZ(val)

    @QtCore.pyqtSlot(int)
    def OptimizeIntervalChanged(self, val):
        self._ins.set_OptimizeInterval(val)

    @QtCore.pyqtSlot(float)
    def PowerLevelOnChanged(self, val):
        self._ins.set_PowerLevelOn(val)

    @QtCore.pyqtSlot(float)
    def StartVoltageChanged(self, val):
        self._ins.set_StartVoltage(val)

    @QtCore.pyqtSlot(float)
    def StepVoltageChanged(self, val):
        self._ins.set_StepVoltage(val)

    @QtCore.pyqtSlot(int)
    def ScanStepsChanged(self, val):
        self._ins.set_ScanSteps(val)

    @QtCore.pyqtSlot(int)
    def ScanCountChanged(self, val):
        self._ins.set_ScanCount(val)

    @QtCore.pyqtSlot(float)
    def InitialWaitChanged(self, val):
        self._ins.set_InitialWait(val)

    @QtCore.pyqtSlot(int)
    def IntegrationTimeChanged(self, val):
        self._ins.set_IntegrationTime(val)

    @QtCore.pyqtSlot(int)
    def LaserInitializeChanged(self, val):
        self._ins.set_LaserInitialize(val)

    @QtCore.pyqtSlot(int)
    def ScanBackChanged(self, val):
        self._ins.set_ScanBack(val)
        enabled_state = self.ui.ScanBack.checkState()
        self.ui.ScanBackTime.setEnabled(enabled_state)

    @QtCore.pyqtSlot(float)
    def ScanBackTimeChanged(self, val):
        self._ins.set_ScanBackTime(val)

    @QtCore.pyqtSlot(int)
    def DCStarkShiftSweepChanged(self, val):
        self._ins.set_DCStarkShiftSweep(val)

    @QtCore.pyqtSlot(int)
    def GateSweepChanged(self, val):
        self._ins.set_GateSweep(val)

    @QtCore.pyqtSlot(int)
    def ModulateGateChanged(self, val):
        self._ins.set_ModulateGate(val)

    @QtCore.pyqtSlot(float)
    def DCStartChanged(self, val):
        self._ins.set_DCStart(val)

    @QtCore.pyqtSlot(float)
    def DCStopChanged(self, val):
        self._ins.set_DCStop(val)

    @QtCore.pyqtSlot(float)
    def DCstepsizeChanged(self, val):
        self._ins.set_DCstepsize(val)

    @QtCore.pyqtSlot(int)
    def PulseDurationChanged(self, val):
        self._ins.set_PulseDuration(val)

    @QtCore.pyqtSlot(int)
    def PulseAOMChanged(self, val):
        self._ins.set_PulseAOM(val)

    @QtCore.pyqtSlot(float)
    def PowerLevelPulseChanged(self, val):
        self._ins.set_PowerLevelPulse(val)

    @QtCore.pyqtSlot(float)
    def PowerLevelScanChanged(self, val):
        self._ins.set_PowerLevelScan(val)

    @QtCore.pyqtSlot(int)
    def WavemeterChannelChanged(self, val):
        self._ins.set_WavemeterChannel(val)

    @QtCore.pyqtSlot(int)
    def CounterChannelChanged(self, val):
        self._ins.set_CounterChannel(val)

    @QtCore.pyqtSlot(int)
    def FrequencyAveragingChanged(self, val):
        self._ins.set_FrequencyAveraging(val)

    @QtCore.pyqtSlot(int)
    def FrequencyInterpolationStepChanged(self, val):
        self._ins.set_FrequencyInterpolationStep(val)

    @QtCore.pyqtSlot(float)
    def FrequencyReferenceChanged(self, val):
        self._ins.set_FrequencyReference(val)

    @QtCore.pyqtSlot(int)
    def ModeHopThresholdChanged(self, val):
        self._ins.set_ModeHopThreshold(val)

    @QtCore.pyqtSlot(int)
    def LaserOnChanged(self, val):
        self._ins.set_LaserOn(val)
        enabled_state = self.ui.LaserOn.checkState()
        self.ui.PiezoVoltage.setEnabled(enabled_state)
        self.ui.ScanVoltage.setEnabled(enabled_state)
        self.ui.SetPiezoVoltage.setEnabled(enabled_state)
        self.ui.SetScanVoltage.setEnabled(enabled_state)

    @QtCore.pyqtSlot(int)
    def DCGateChanged(self, val):
        self._ins.set_DCGate(val)

#    @QtCore.pyqtSlot()
    def CommentsChanged(self):
        self._ins.set_Comments(self.ui.Comments.toPlainText())

    @QtCore.pyqtSlot(bool)
    def SetScanVoltage(self, bool):
        self._ins.set_ScanVoltage(self.ui.ScanVoltage.value())

    @QtCore.pyqtSlot(bool)
    def SetPiezoVoltage(self,bool):
        self._ins.set_PiezoVoltage(self.ui.PiezoVoltage.value())

    @QtCore.pyqtSlot(bool)
    def SetGate1Voltage(self, bool):
        self._ins.set_Gate1Voltage(self.ui.Gate1Voltage.value())

    @QtCore.pyqtSlot(bool)
    def SetGate2Voltage(self, bool):
        self._ins.set_Gate2Voltage(self.ui.Gate2Voltage.value())

    @QtCore.pyqtSlot(int)
    def LockFrequencyChanged(self, val):
        self._ins.set_LockFrequency(val)

    @QtCore.pyqtSlot(int)
    def XYScanIndexChanged(self, val):
        if val > 0:
            print('XYScanIndexChanged : (1)')
            self.ui.trace_singlescan_XY.reset()
            print('XYScanIndexChanged : (2)')
            temp = numpy.array(self._frequency_history[val-1])*1000 - self.ui.FrequencyReference.value()
            print('XYScanIndexChanged : (3)')
            self.ui.trace_singlescan_XY.add_points_xy(temp.tolist(),self._counts_history[val-1])
            print('XYScanIndexChanged : (4)')
        else:
            print('XYScanIndexChanged : (8)')
            if len(self._current_frequency) > 0:
                print('XYScanIndexChanged : (6)')
                self.ui.trace_singlescan_XY.reset()
                print('XYScanIndexChanged : (7)')
                temp = self._current_frequency*1000 - self.ui.FrequencyReference.value()
                print('XYScanIndexChanged : (8)')
                self.ui.trace_singlescan_XY.add_points_xy(temp.tolist(),self._current_counts.tolist())
                print('XYScanIndexChanged : (9)')

    @QtCore.pyqtSlot(float)
    def FrequencySetpointChanged(self, val):
        if self._stepping == True:
            self._stepping = False
        else:
            self._ins.set_LockFrequency(False)
        self._ins.set_FrequencySetpoint(val + self.ui.FrequencyReference.value())

    @QtCore.pyqtSlot(int)
    def FrequencyStepChanged(self, val):
        self._ins.set_FrequencyStep(val)

    @QtCore.pyqtSlot(bool)
    def StepUp(self, bool):
        self._stepping = True
        self._ins.set_FrequencySetpoint(self._ins.get_FrequencySetpoint() + self._ins.get_FrequencyStep()/1000.0)

    @QtCore.pyqtSlot(bool)
    def StepDown(self, bool):
        self._stepping = True
        self._ins.set_FrequencySetpoint(self._ins.get_FrequencySetpoint() - self._ins.get_FrequencyStep()/1000.0)

    def StartScan(self, val):
        self._ins.start_scan()

    def PauseScan(self, val):
        self._ins.pause_scan()

    def AbortScan(self, val):
        self._ins.abort_scan()

    def PulseAOM_manual(self, val):
        self._ins.PulseAOM_manual()

    def SkipToNext(self, val):
        self._ins.SkipToNext()

    def _instrument_changed(self, changes):
        if changes.has_key('StartVoltage'):
            self.ui.StartVoltage.setValue(changes['StartVoltage'])
        if changes.has_key('StepVoltage'):
            self.ui.StepVoltage.setValue(changes['StepVoltage'])
        if changes.has_key('ScanSteps'):
            self.ui.ScanSteps.setValue(changes['ScanSteps'])
        if changes.has_key('ScanCount'):
            self.ui.ScanCount.setValue(changes['ScanCount'])
        if changes.has_key('InitialWait'):
            self.ui.InitialWait.setValue(changes['InitialWait'])
        if changes.has_key('IntegrationTime'):
            self.ui.IntegrationTime.setValue(changes['IntegrationTime'])
        if changes.has_key('LaserInitialize'):
            self.ui.LaserInitialize.setChecked(changes['LaserInitialize'])
        if changes.has_key('ScanBack'):
            self.ui.ScanBack.setChecked(changes['ScanBack'])
            enabled_state = self.ui.ScanBack.checkState()
            self.ui.ScanBackTime.setEnabled(enabled_state)
        if changes.has_key('ScanBackTime'):
            self.ui.ScanBackTime.setValue(changes['ScanBackTime'])
        if changes.has_key('DCStarkShiftSweep'):
            self.ui.DCStarkShiftSweep.setChecked(changes['DCStarkShiftSweep'])
        if changes.has_key('GateSweep'):
            self.ui.GateSweep.setChecked(changes['GateSweep'])
            enabled_state = not(self.ui.GateSweep.checkState())
            self.ui.StartVoltage.setEnabled(enabled_state)
            self.ui.StepVoltage.setEnabled(enabled_state)
            self.ui.LaserInitialize.setEnabled(enabled_state)
            self.ui.ModulateGate.setEnabled(not(enabled_state))
            self.ui.DCStarkShiftSweep.setEnabled(enabled_state)
            self.ui.ScanSteps.setEnabled(enabled_state)
            self.ui.ScanBack.setEnabled(enabled_state)
            self.ui.ScanBackTime.setEnabled(enabled_state)
        if changes.has_key('DCStart'):
            self.ui.DCStart.setValue(changes['DCStart'])
        if changes.has_key('DCStop'):
            self.ui.DCStop.setValue(changes['DCStop'])
        if changes.has_key('DCstepsize'):
            self.ui.DCstepsize.setValue(changes['DCstepsize'])
        if changes.has_key('PulseAOM'):
            self.ui.PulseAOM.setChecked(changes['PulseAOM'])
        if changes.has_key('PulseDuration'):
            self.ui.PulseDuration.setValue(changes['PulseDuration'])
        if changes.has_key('PowerLevelPulse'):
            self.ui.PowerLevelPulse.setValue(changes['PowerLevelPulse'])
        if changes.has_key('PowerLevelScan'):
            self.ui.PowerLevelScan.setValue(changes['PowerLevelScan'])
        if changes.has_key('WavemeterChannel'):
            self.ui.WavemeterChannel.setValue(changes['WavemeterChannel'])
        if changes.has_key('CounterChannel'):
            self.ui.CounterChannel.setValue(changes['CounterChannel'])
        if changes.has_key('FrequencyAveraging'):
            self.ui.FrequencyAveraging.setValue(changes['FrequencyAveraging'])
        if changes.has_key('FrequencyInterpolationStep'):
            self.ui.FrequencyInterpolationStep.setValue(changes['FrequencyInterpolationStep'])
        if changes.has_key('FrequencyReference'):
            self.ui.FrequencyReference.setValue(changes['FrequencyReference'])
        if changes.has_key('ModeHopThreshold'):
            self.ui.ModeHopThreshold.setValue(changes['ModeHopThreshold'])
        if changes.has_key('LaserOn'):
            self.ui.LaserOn.setChecked(changes['LaserOn'])
            enabled_state = self.ui.LaserOn.checkState()
            self.ui.PiezoVoltage.setEnabled(enabled_state)
            self.ui.ScanVoltage.setEnabled(enabled_state)
            self.ui.SetPiezoVoltage.setEnabled(enabled_state)
            self.ui.SetScanVoltage.setEnabled(enabled_state)
        if changes.has_key('DCGate'):
            self.ui.DCGate.setValue(changes['DCGate'])
        if changes.has_key('CurrentFrequency'):
            self.ui.CurrentFrequency.setValue(changes['CurrentFrequency'])
            self.ui.RelativeFrequency.setValue(changes['CurrentFrequency']-self.ui.FrequencyReference.value())
            self._ins.get_LockFrequencyDeviation()

        if changes.has_key('ScanVoltage'):
            self.ui.ScanVoltage.setValue(changes['ScanVoltage'])
        if changes.has_key('PiezoVoltage'):
            self.ui.PiezoVoltage.setValue(changes['PiezoVoltage'])
        if changes.has_key('Gate1Voltage'):
            self.ui.Gate1Voltage.setValue(changes['Gate1Voltage'])
        if changes.has_key('Gate2Voltage'):
            self.ui.Gate2Voltage.setValue(changes['Gate2Voltage'])
        if changes.has_key('LockFrequency'):
            self.ui.LockFrequency.setChecked(changes['LockFrequency'])
            enabled_state = self.ui.LockFrequency.checkState()
            self.ui.FrequencyStep.setEnabled(enabled_state)
            self.ui.StepUp.setEnabled(enabled_state)
            self.ui.StepDown.setEnabled(enabled_state)
        if changes.has_key('LockFrequencyDeviation'):
            self.ui.LockFrequencyDeviation.setValue(changes['LockFrequencyDeviation'])
        if changes.has_key('FrequencySetpoint'):            
            self.ui.FrequencySetpoint.setValue(changes['FrequencySetpoint'] - self.ui.FrequencyReference.value())
        if changes.has_key('FrequencyStep'):
            self.ui.FrequencyStep.setValue(changes['FrequencyStep'])
        if changes.has_key('TraceIndex'): # Remove underscores to re-enable real-time plotting in cyclops
            if self._blocked == 0:
                self._blocked = 1
                self._new_index = changes['TraceIndex']
                if (self._new_index >= self._CurrentTraceIndex + 10):
                    counts = numpy.array(self._ins.data_counts_trace(self._CurrentScanIndex, self._CurrentTraceIndex, self._new_index - self._CurrentTraceIndex))
                    frequency = numpy.array(self._ins.data_frequency_trace(self._CurrentScanIndex, self._CurrentTraceIndex, self._new_index - self._CurrentTraceIndex))

                    if self._CurrentTraceIndex == 0:
                        self._current_counts    = counts
                        self._current_frequency = frequency
                    else:
                        self._current_counts    = numpy.append(self._current_counts,counts)
                        self._current_frequency = numpy.append(self._current_frequency,frequency)

                    self.ui.trace_counts.add_points(counts.tolist())
                    temp = frequency*1000 - self.ui.FrequencyReference.value()
                    self.ui.trace_frequency.add_points(temp.tolist())
                    if self.ui.XYScanIndex.value() == 0:
                        self.ui.trace_singlescan_XY.add_points_xy(temp.tolist(),counts.tolist())
    
                    self._CurrentTraceIndex = self._new_index
                self._blocked = 0
# Remove underscores to re-enable real-time plotting in cyclops
        if changes.has_key('ScanIndex'):
            while self._blocked == 1:
                time.sleep(0.001)

            self._blocked = 1

            if changes['ScanIndex'] < self.ui.ScanCount.value():
                self.ui.CurrentScan.setValue(changes['ScanIndex']+1)
            if self.ui.XYScanIndex.value() == 0:
                self.ui.trace_frequency.reset()
                self.ui.trace_counts.reset()
                self.ui.trace_singlescan_XY.reset()
            self._CurrentScanIndex = changes['ScanIndex']
            self._CurrentTraceIndex = 0
            if changes['ScanIndex'] == 0:
                self._trace_finished = -1
            self._blocked = 0

# Remove underscores to re-enable real-time plotting in cyclops
        if changes.has_key('TraceFinished'):
            while self._blocked == 1:
                time.sleep(0.001)

            self._blocked = 1

            packet_size = 1000

            self._trace_finished = changes['TraceFinished']
            self.ui.XYScanIndex.setMaximum(max(0,self._trace_finished+1))

            if self._trace_finished == 0:
                data = numpy.array([])
                length = self.ui.ScanSteps.value()
                packets = length/packet_size
                for i in range(0,packets):
                    data = numpy.append(data,numpy.array(self._ins.data_counts_trace(self._trace_finished,i*packet_size,packet_size)))
                if packets*packet_size < length:
                    data = numpy.append(data,numpy.array(self._ins.data_counts_trace(self._trace_finished,packets*packet_size,length-packets*packet_size)))
                self._counts_history = [data.tolist()]

                data = numpy.array([])
                for i in range(0,packets):
                    data = numpy.append(data,numpy.array(self._ins.data_frequency_trace(self._trace_finished,i*packet_size,packet_size)))
                if packets*packet_size < length:
                    data = numpy.append(data,numpy.array(self._ins.data_frequency_trace(self._trace_finished,packets*packet_size,length-packets*packet_size)))
                self._frequency_history = [data.tolist()]

                data2D_size = self._ins.data2D_size()
                data = numpy.array([])

                packets = data2D_size/packet_size
                for i in range(0,packets):
                    print(' -> *')
                    data = numpy.append(data,numpy.array(self._ins.partial_data2D(self._trace_finished,i*packet_size,packet_size)))
                    print('    * <- ')

                if packets*packet_size < data2D_size:
                    print(' -> +')
                    data = numpy.append(data,numpy.array(self._ins.partial_data2D(self._trace_finished,packets*packet_size,data2D_size-packets*packet_size)))
                    print('    + <- ')

                self._data2D = [data.tolist()]
                self._data2D.append(numpy.zeros(data2D_size).tolist())
                self.ui.plot_2D.set_data(self._data2D, range(0,2), range(0,data2D_size))
                self._data2D = [self._data2D[0]]    

            elif self._trace_finished > 0:
                data = numpy.array([])
                length = self.ui.ScanSteps.value()
                packets = length/packet_size
                for i in range(0,packets):
                    data = numpy.append(data,numpy.array(self._ins.data_counts_trace(self._trace_finished,i*packet_size,packet_size)))
                if packets*packet_size < length:
                    data = numpy.append(data,numpy.array(self._ins.data_counts_trace(self._trace_finished,packets*packet_size,length-packets*packet_size)))
#                print('counts:')
#                print(data)
                self._counts_history.append(data.tolist())

                data = numpy.array([])
                for i in range(0,packets):
                    data = numpy.append(data,numpy.array(self._ins.data_frequency_trace(self._trace_finished,i*packet_size,packet_size)))
                if packets*packet_size < length:
                    data = numpy.append(data,numpy.array(self._ins.data_frequency_trace(self._trace_finished,packets*packet_size,length-packets*packet_size)))
#                print('frequency:')
#                print(data)
                self._frequency_history.append(data.tolist())

                data2D_size = self._ins.data2D_size()
                data = numpy.array([])

                packets = data2D_size/packet_size
                for i in range(0,packets):
                    print(' -> x')
                    data = numpy.append(data,numpy.array(self._ins.partial_data2D(self._trace_finished,i*packet_size,packet_size)))
                    print('    x <- ')

                if packets*packet_size < data2D_size:
                    print(' -> #')
                    data = numpy.append(data,numpy.array(self._ins.partial_data2D(self._trace_finished,packets*packet_size,data2D_size-packets*packet_size)))
                    print('    # <- ')

                self._data2D.append(data.tolist())
                self.ui.plot_2D.set_data(self._data2D, range(0,self._trace_finished+1), range(0,data2D_size))

            self._blocked = 0




        if changes.has_key('MWOn'):
            self.ui.MWOn.setChecked(changes['MWOn'])
            enabled_state = self.ui.MWOn.checkState()
            self.ui.MWfrequency.setEnabled(enabled_state)
            self.ui.MWpower.setEnabled(enabled_state)
            self.ui.SetMWfrequency.setEnabled(enabled_state)
            self.ui.SetMWpower.setEnabled(enabled_state)
        if changes.has_key('MWfrequency'):
            self.ui.MWfrequency.setValue(changes['MWfrequency']/1e9)
        if changes.has_key('MWpower'):
            self.ui.MWpower.setValue(changes['MWpower'])
        if changes.has_key('PowerLevelOn'):
            self.ui.PowerLevelOn.setValue(changes['PowerLevelOn'])
        if changes.has_key('AutoOptimizeXY'):
            self.ui.AutoOptimizeXY.setChecked(changes['AutoOptimizeXY'])
        if changes.has_key('AutoOptimizeZ'):
            self.ui.AutoOptimizeZ.setChecked(changes['AutoOptimizeZ'])
        if changes.has_key('OptimizeInterval'):
            self.ui.OptimizeInterval.setValue(changes['OptimizeInterval'])


    def timerEvent(self, event):
        Panel.timerEvent(self, event)
        self._ins.get_CurrentFrequency(callback=self._frequency_cb)
        self.ui.chart_frequency.set_scale_tightfit()

    def _frequency_cb(self, cr, *args):
        self.ui.chart_frequency.add_point(cr-self.ui.FrequencyReference.value())
            
