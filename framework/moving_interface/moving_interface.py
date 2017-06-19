from utils import *


class Moving_Interface:
    __metaclass__ = Singleton

    def move_to(self, position):
        print("[!!] We are moving to "+str(position)+" (to be replaced with interface code)")


global moving_interface = Moving_Interface()
