
#Temporary AX12 and Moving_Interface classes

from threading import Thread
import time


class AX12:

    def __init__(self, id):
        self.id = id

    def move_to(self, position=(0,0), callback=None):
        print("[!!] We are moving in AX12 "+str(self.id)+" to "+str(position)+" (to be replaced with interface code)")
        self.callback = callback
        t = Thread(target=lambda: self.run()).start()

    def run(self):
        time.sleep(2.5)
        if self.callback is not None:
            self.callback()


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Moving_Interface:
    __metaclass__ = Singleton

    def move_to(self, robot, position):
        print("[!!!] We are moving to "+str(position)+" (to be replaced with interface code)")


moving_interface = Moving_Interface()
