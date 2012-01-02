# Main controller for RT2 to observe all kind of stuff
# 
# Author: Wolfgang Pfaff <w.pfaff@tudelft.nl>
import numpy
from panel import Panel
from ui_rt2_coordinator import Ui_Panel
from PyQt4 import QtCore
from lib.network.object_sharer import helper

class RT2CoordinatorPanel(Panel):

    # Front
    front_z_slide_changed = QtCore.pyqtSignal(int)
    front_z_changed = QtCore.pyqtSignal(float)

    # Back
    back_z_slide_changed = QtCore.pyqtSignal(int)
    back_z_changed = QtCore.pyqtSignal(float)

    # Stage
    stage_x_changed = QtCore.pyqtSignal(float)
    stage_y_changed = QtCore.pyqtSignal(float)

    # Back SM
    back_x_changed = QtCore.pyqtSignal(float)
    back_y_changed = QtCore.pyqtSignal(float)

    # Det SM
    detsm_x_changed = QtCore.pyqtSignal(float)
    detsm_y_changed = QtCore.pyqtSignal(float)

    # Other
    keyword_changed = QtCore.pyqtSignal(str)

    
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui  
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        # set values from instruments
        # Front
        self.ui.front_z.setValue(self._ins.get_mos_front_z())
        self.ui.front_z_slider.setValue(int(self._ins.get_mos_front_z()*10))

        # Back
        self.ui.back_z.setValue(self._ins.get_mos_back_z())
        self.ui.back_z_slider.setValue(int(self._ins.get_mos_back_z()*10))

        # Stage
        self.ui.stage_x.setValue(self._ins.get_mos_stage_x())
        self.ui.stage_y.setValue(self._ins.get_mos_stage_y())

        # Back
        self.ui.back_x.setValue(self._ins.get_mos_rearsm_x())
        self.ui.back_y.setValue(self._ins.get_mos_rearsm_y())

        # Detsm
        self.ui.detsm_x.setValue(self._ins.get_mos_detsm_x())
        self.ui.detsm_y.setValue(self._ins.get_mos_detsm_y())

        # Other
        self.ui.keyword.setText(self._ins.get_keyword())

    # Slots
    # Front
    def new_front_z(self):
        self._ins.set_mos_front_z(self.ui.front_z.value())
        self.ui.front_z_slider.setValue(int(self._ins.get_mos_front_z()*10))

    def slide_front_z(self, val):
        self._ins.set_mos_front_z(val/10., callback=None)
        self.ui.front_z.setValue(val/10.)

    # Back
    def new_back_z(self):
        self._ins.set_mos_back_z(self.ui.back_z.value())
        self.ui.back_z_slider.setValue(int(self._ins.get_mos_back_z()*10))

    def slide_back_z(self, val):
        self._ins.set_mos_back_z_position(val/10., callback=None)
        self.ui.back_z.setValue(val/10.)

    # Stage
    def new_stage_x(self):
        self._ins.set_mos_stage_x(self.ui.stage_x.value())

    def new_stage_y(self):
        self._ins.set_mos_stage_y(self.ui.stage_y.value())

    def stage_up(self):
        step = self.ui.stage_step.value()
        self._ins.mos_step_stage_y(step)

    def stage_down(self):
        step = self.ui.stage_step.value()
        self._ins.mos_step_stage_y(-step)

    def stage_left(self):
        step = self.ui.stage_step.value()
        self._ins.mos_step_stage_x(-step)

    def stage_right(self):
        step = self.ui.stage_step.value()
        self._ins.mos_step_stage_x(step)
        
    # Back
    def new_back_x(self):
        self._ins.set_mos_rearsm_x(self.ui.back_x.value())

    def new_back_y(self):
        self._ins.set_mos_rearsm_y(self.ui.back_y.value())

    def back_up(self):
        step = self.ui.back_step.value()
        self._ins.mos_step_rearsm_y(step)

    def back_down(self):
        step = self.ui.back_step.value()
        self._ins.mos_step_rearsm_y(-step)

    def back_left(self):
        step = self.ui.back_step.value()
        self._ins.mos_step_rearsm_x(-step)

    def back_right(self):
        step = self.ui.back_step.value()
        self._ins.mos_step_rearsm_x(step)

    # Detsm
    def new_detsm_x(self):
        self._ins.set_mos_detsm_x(self.ui.detsm_x.value())

    def new_detsm_y(self):
        self._ins.set_mos_detsm_y(self.ui.detsm_y.value())

        
    # Other
    def toggle_spectrometer_bs(self):
        self._ins.bs_spectrometer_toggle(callback=None)

    def toggle_rear_det_bs(self):
        self._ins.bs_rear_det_toggle(callback=None)

    def toggle_pulsed_laser_bs(self):
        self._ins.bs_pulsed_laser_toggle(callback=None)

    def set_keyword(self, val):
        self._ins.set_keyword(val)

        
    # internal functions
    def _instrument_changed(self, changes):
        keys = {'mos_stage_x': getattr(self.ui.stage_x, 'setValue'),
                'mos_stage_y': getattr(self.ui.stage_y, 'setValue'),
                'mos_detsm_x': getattr(self.ui.detsm_x, 'setValue'),
                'mos_detsm_y': getattr(self.ui.detsm_y, 'setValue'),
                'mos_rearsm_x': getattr(self.ui.back_x, 'setValue'),
                'mos_rearsm_y': getattr(self.ui.back_y, 'setValue'),
                'mos_front_z': getattr(self, '_ui_set_front_z'),
                'mos_back_z': getattr(self, '_ui_set_back_z'),
                'keyword': getattr(self.ui.keyword, 'setText')
                }

        for k in changes:
            try:
                keys[k](changes[k])
            except KeyError:
                pass

    def _ui_set_front_z(self, z):
        self.ui.front_z.setValue(z)
        self.ui.front_z_slider.setValue(int(z*10))
        pass

    def _ui_set_back_z(self, z):
        self.ui.back_z.setValue(z)
        self.ui.back_z_slider.setValue(int(z*10))
        pass

    # every time the panel timer is called, we update the plot data with
    # the locally cached data
    def timerEvent(self, event):
        pass


            
