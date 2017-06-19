from utils import *
import time


class AX12:

    def __init__(self, id):
        self.id = id

    def move_to(self, position, callback=None):
        print("[!!] We are moving in AX12 "+str(self.id)+" to "+str(position)+" (to be replaced with interface code)")
        self.callback = callback
        t = Thread(target=lambda: self.run())

    def run(self):
        time.sleep(0.5)
        if self.callback is not None:
            self.callback()
