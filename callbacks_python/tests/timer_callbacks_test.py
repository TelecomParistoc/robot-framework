import random
import ctypes
import time


def common_callback(index, time):
	print "Callback with index "+str(index)+" reached after a "+str(time)+" seconds delay"

def nulle():
	print "NUl"

def timer_launch(time, index, lib):
	return lib.call_after_delay(ctypes.c_float(time), ctypes.CFUNCTYPE(None)(nulle))
	return lib.call_after_delay(ctypes.c_float(time), ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_float)(common_callback), ctypes.c_int(index), ctypes.c_float(time))

lib = ctypes.cdll.LoadLibrary("/home/pi/robot-framework/callbacks_python/tests/timer_callbacks_test.so")

n_callbacks = 20

for i in range(n_callbacks):
	timer_launch(float(random.randint(10,1000)/50.0), i, lib)

while int(lib.empty_queue_callback()) == 0:
	print(lib.local_exported_queue_size())
	time.sleep(0.01)

lib.join()