from panel import Panel
from ui_command0r_panel import Ui_Panel

from PyQt4 import QtCore

class Command0rPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # UI
        self.ui = Ui_Panel()
        self.ui.setupUi(self, evalfunc=self._ins.evaluate,
                execfunc=self._ins.execute)


