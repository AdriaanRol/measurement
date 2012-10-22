from instrument import Instrument
import types
import qt

# TODO add command history
# TODO redirect output: http://stackoverflow.com/questions/3906232/python-get-the-print-output-in-an-exec-statement

class command0r(Instrument):
    """
    this is a simple instrument that can execute a string as a python
    command. useful to have the ability to enter commands via a textfield
    from a gui client.
    """

    def __init__(self, name):
        Instrument.__init__(self,name)
        self.name = name

        self.add_function('execute')
        self.add_function('evaluate')

    def execute(self, cmd):
        print "%s about to execute: %s" % (self.name, cmd)
        exec(cmd)
        return

    def evaluate(self, cmd):
        print "%s about to evaluate: %s" % (self.name, cmd)
        ret = eval(cmd)
        print "return value: %s" % (ret)
        return ret


