# lt2_coordinator_panel.py
#
# auto-created by ..\..\..\cyclops\tools\ui2cyclops.py v20110215, Fri Jan 13 13:19:35 2012

from panel import Panel
from ui_lt2_coordinator_panel import Ui_Panel

from PyQt4 import QtCore

class Lt2Coordinator(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        self.ui.keyword.setText(self._ins.get_keyword())
        self.ui.x.setValue(self._ins.get_x())
        self.ui.y.setValue(self._ins.get_y())
        self.ui.z.setValue(self._ins.get_z())
        self.ui.z_slider.setValue(self._ins.get_z_slider())
        self.ui.step.setValue(self._ins.get_step())

        self.ui.keyword.textEdited.connect(self._set_keyword)
        self.ui.x.valueChanged.connect(self._set_x)
        self.ui.y.valueChanged.connect(self._set_y)
        self.ui.z.valueChanged.connect(self._set_z)
        self.ui.z_slider.sliderMoved.connect(self._set_z_slider)
        self.ui.step.valueChanged.connect(self._set_step)

        self.ui.step_up.pressed.connect(self._step_up)
        self.ui.step_left.pressed.connect(self._step_left)
        self.ui.step_right.pressed.connect(self._step_right)
        self.ui.step_down.pressed.connect(self._step_down)

    def _step_up(self):
        self._ins.step_up()
        return

    def _step_left(self):
        self._ins.step_left()
        return

    def _step_right(self):
        self._ins.step_right()
        return

    def _step_down(self):
        self._ins.step_down()
        return

    def _set_keyword(self, val):
        self._ins.set_keyword(val)
        return

    def _set_x(self, val):
        self._ins.set_x(val)
        return

    def _set_y(self, val):
        self._ins.set_y(val)
        return

    def _set_z(self, val):
        self._ins.set_z(val)
        return

    def _set_z_slider(self, val):
        self._ins.set_z_slider(val)
        return

    def _set_step(self, val):
        self._ins.set_step(val)
        return

    def _instrument_changed(self, changes):
         keys = {'mos_x': getattr(self.ui.x, 'setValue'),
                'mos_y': getattr(self.ui.y, 'setValue'),
                #'mos_detsm_x': getattr(self.ui.detsm_x, 'setValue'),
                #'mos_detsm_y': getattr(self.ui.detsm_y, 'setValue'),
                #'mos_rearsm_x': getattr(self.ui.back_x, 'setValue'),
                #'mos_rearsm_y': getattr(self.ui.back_y, 'setValue'),
                'mos_z': getattr(self, '_ui_set_z'),
                #'mos_back_z': getattr(self, '_ui_set_back_z'),
                'keyword': getattr(self.ui.keyword, 'setText')
                }

        for k in changes:
            try:
                keys[k](changes[k])
            except KeyError:
                pass

    def _ui_set_z(self, z):
        self.ui.z.setValue(z)
        self.ui.z_slider.setValue(int(z*10))
        pass

