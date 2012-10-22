from PyQt4 import QtCore, QtGui

class Ui_Panel(object):
    def setupUi(self, Panel, evalfunc, execfunc):
        Panel.setObjectName("Panel")
        Panel.resize(500,500)

        self.evalfunc = evalfunc
        self.execfunc = execfunc
        self.cmdlines = {}
        
        self.add_button = QtGui.QPushButton('add')
        self.add_button.pressed.connect(self.add_cmdline)

        self.layout = QtGui.QVBoxLayout(Panel)
        self.layout.setObjectName('layout')
        self.layout.addWidget(self.add_button)

    def add_cmdline(self):
        linelayout = QtGui.QHBoxLayout()
        cmdline = QtGui.QLineEdit()
        evalbutton = QtGui.QPushButton('eval')
        execbutton = QtGui.QPushButton('exec')
        delbutton = QtGui.QPushButton('-')      
        
        if len(self.cmdlines) == 0:
            number = 0
        else:
            number = max([c for c in self.cmdlines]) + 1
        self.cmdlines[number] = {
                'cmdline' : cmdline,
                'evalbutton' : evalbutton,
                'execbutton' : execbutton,
                'delbutton' : delbutton, 
                'layout' : linelayout, }        
        
        linelayout.addWidget(cmdline)
        linelayout.addWidget(evalbutton)
        linelayout.addWidget(execbutton)
        linelayout.addWidget(delbutton)
        self.layout.addLayout(linelayout)

        def remove_cmdline():
            linelayout.removeWidget(cmdline)
            linelayout.removeWidget(evalbutton)
            linelayout.removeWidget(execbutton)
            linelayout.removeWidget(delbutton)
            self.layout.removeItem(linelayout)
            self.cmdlines[number]['evalbutton'].deleteLater()
            self.cmdlines[number]['evalbutton'] = None
            self.cmdlines[number]['execbutton'].deleteLater()
            self.cmdlines[number]['execbutton'] = None
            self.cmdlines[number]['delbutton'].deleteLater()
            self.cmdlines[number]['delbutton'] = None
            self.cmdlines[number]['cmdline'].deleteLater()
            self.cmdlines[number]['cmdline'] = None
            self.cmdlines[number]['layout'].deleteLater()
            self.cmdlines[number]['layout'] = None
            del self.cmdlines[number]

        delbutton.pressed.connect(remove_cmdline)

        def evaluate():
            cmd = self.cmdlines[number]['cmdline'].text()
            self.evalfunc(cmd)

        evalbutton.pressed.connect(evaluate)

        def execute():
            cmd = self.cmdlines[number]['cmdline'].text()
            self.execfunc(cmd)

        execbutton.pressed.connect(execute)




        

