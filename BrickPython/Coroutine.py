# Scheduler
# Support for coroutines using Python generator functions.
#
# Copyright (c) 2014 Charles Weir.  Shared under the MIT Licence.

import logging
import sys, traceback
import threading
import datetime

class StopCoroutineException( Exception ):
    '''Exception used to stop a coroutine'''
    pass

ProgramStartTime = datetime.datetime.now()

class Coroutine( threading.Thread ):
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.logger = logging
        self.mySemaphore = threading.Semaphore(0)
        self.callerSemaphore = threading.Semaphore(0)
        self.stopEvent = threading.Event()
        self.setDaemon(True) # Daemon threads don't prevent the process from exiting.
        self.func = func
        self.lastExceptionCaught = None
        self.start()

    @staticmethod
    def currentTimeMillis():
        'Answers the time in floating point milliseconds since program start.'
        global ProgramStartTime
        c = datetime.datetime.now() - ProgramStartTime
        return c.days * (3600.0 * 1000 * 24) + c.seconds * 1000.0 + c.microseconds / 1000.0

    def run(self):
        try:
            self.mySemaphore.acquire()
            self.func(*self.args,**self.kwargs)
        except (StopCoroutineException, StopIteration):
            pass
        except Exception as e:
            self.lastExceptionCaught = e
            self.logger.info( "Coroutine - caught exception: %r" % (e) )
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = "".join(traceback.format_tb(exc_traceback))
            self.logger.debug( "Traceback (latest call first):\n %s" % trace )
        self.callerSemaphore.release()
        threading.Thread.run(self) # Does some cleanup.

    def call(self):
        'Executed from the caller thread.  Runs the coroutine until it calls wait. Does nothing if the thread has terminated.'
        if self.isAlive():
            self.mySemaphore.release()
            self.callerSemaphore.acquire()

    def stop(self):
        'Executed from the caller thread.  Stops the coroutine, causing thread to terminate.'
        self.stopEvent.set()
        self.call()

    @staticmethod
    def wait():
        'Called from within the coroutine to hand back control to the caller thread'
        self=threading.currentThread()
        self.callerSemaphore.release()
        self.mySemaphore.acquire()
        if (self.stopEvent.isSet()):
            raise StopCoroutineException()

    @staticmethod
    def waitMilliseconds(timeMillis):
        'Called from within the coroutine to wait the given time'
        startTime = Coroutine.currentTimeMillis()
        while Coroutine.currentTimeMillis() - startTime < timeMillis:
            Coroutine.wait()

#             while not self.stopEvent.is_set():

#
#         self.scheduler.coroutines.remove( self )
#         self.scheduler.semaphore.release()

class GeneratorCoroutineWrapper(Coroutine):
    '''Internal: Wraps a generator-style coroutine with a thread'''

    def __init__(self, scheduler, generator):
        '''`scheduler` - the main Scheduler object
        `generator` - the generator object created by calling the generator function'''
        Coroutine.__init__(self)
        self.scheduler = scheduler
        self.stopEvent = threading.Event()
        self.generator = generator
        self.thread = threading.Thread(target=self.action)
        self.thread.setDaemon(True) # Daemon threads don't prevent the process from exiting.
        self.thread.start()

    def action(self):
        'The thread entry function - executed within thread `thread`'
        try:
            self.semaphore.acquire()
            while not self.stopEvent.is_set():
                self.generator.next()
                self.scheduler.semaphore.release()
                self.semaphore.acquire()
            self.generator.throw(StopCoroutineException)
        except (StopCoroutineException, StopIteration):
            pass
        except Exception as e:
            self.scheduler.lastExceptionCaught = e
            logging.info( "Scheduler - caught: %r" % (e) )
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = "".join(traceback.format_tb(exc_traceback))
            logging.debug( "Traceback (latest call first):\n %s" % trace )

        self.scheduler.coroutines.remove( self )
        self.scheduler.semaphore.release()

    def next(self):
        'Runs a bit of processing (next on the generator) - executed from the scheduler thread - returns only when processing has completed'
        self.semaphore.release()
        self.scheduler.semaphore.acquire()

    def stop(self):
        'Causes the thread to stop - executed from the scheduler thread'
        self.stopEvent.set()

