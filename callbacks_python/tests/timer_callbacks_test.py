import random
import ctypes
import time


def common_callback(index, time):
	print "Callback with index "+str(index)+" reached after a "+str(time)+" seconds delay"

def timer_launch(callback, time, index, lib):
	assert(callable(callback))
	return lib.call_after_delay(time, lambda: callback(index, time))

lib = ctypes.cdll.LoadLibrary("timer_callbacks.so")

n_callbacks = 20

for i in range(n_callbacks):
	timer_launch(common_callback, float(random.randomint(10,1000)/50.0), i, lib)

while int(lib.empty_queue_callback()) == 0:
	time.sleep(0.01)
