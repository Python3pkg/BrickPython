# App
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import sys, os # Python path kludge - omit these 2 lines if BrickPython is installed.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from BrickPython.TkApplication import TkApplication
from BrickPython.Sensor import Sensor
import logging

class App(TkApplication):
    '''Application to
    '''

    def __init__(self):
        TkApplication.__init__(self, {'1': Sensor.ULTRASONIC_CONT })
        self.doorLocked = False
        self.addSensorCoroutine( self.turnWhenDetected() )
        self.root.wm_title("Trial running")
        for c in "ABCD":
            self.motor(c).zeroPosition()

    def turnWhenDetected(self):
        while True:
            for i in self.waitMilliseconds(500): yield
            print self.sensor('4').value()


##        for c in "ABCD":
##            motor= self.motor(c)
##            for i in motor.moveTo(90*2): yield
##            for i in motor.moveTo(0): yield
##

if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.DEBUG) # All log messages printed to console.
    logging.info( "Starting" )
    app = App()
    app.mainloop()