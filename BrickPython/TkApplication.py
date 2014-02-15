# TkApplication class.  Brings together the Tk GUI functionality, the Scheduler and the BrickPi wrapper.
# Applications using the BrickPi derive from this, implementing appropriate functionality.


import Tkinter as tk

from BrickPiWrapper import *
from Motor import *


# TODO: How to stop two coroutines running at once on the same port?

# Main application class.  I'm not usually keen on multiple inheritance, but it makes using it much simpler.


class TkApplication(BrickPiWrapper):

    # Parameter: Configuration, e.g. {PORT_1: TYPE_SENSOR_ULTRASONIC_CONT } as passed to BrickPiWrapper
    def __init__(self, sensorConfiguration):
        BrickPiWrapper.__init__(self, sensorConfiguration )
        self.root = tk.Tk()

        self.doInitialization()

        self.pidSetting = PIDSetting()
        self.timerTick()
        self.addUpdateCoroutine( self.updaterCoroutine() )

    # Default initialization function with a simple window - override if you want something different
    def doInitialization(self):
        self.root.geometry('300x200')
        self.label = tk.Label(text="BrickPi")
        self.label.pack()
        self.root.bind('<KeyPress>', self.onKeyPress)


    # The main loop for the application - call this after initialization.  Returns on exit.
    def mainloop(self):
        self.root.mainloop()

    # Private: Does all the coroutine processing, every 20ms or so.
    def timerTick(self):
        self.doWork()
        self.root.after(int(self.timeMillisToNextCall()), self.timerTick)

    # Default key press handling - answers True if it's handled the key.
    # Override this function to add extra keypress handling.
    def onKeyPress(self, event):
        char = event.char
        if char == "": # Key such as shift or control...
            pass
        elif(char=='q'):
            self.root.destroy()
        else:
            return False
        return True
