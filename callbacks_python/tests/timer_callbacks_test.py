#!/usr/bin/python
#coding: utf8

import random
import ctypes
import time


def common_callback(index, time):
	print "Callback with index "+str(index)+" reached after a "+str(time)+" seconds delay"

func = []
def timer_launch(time, index, lib):
	func.append(ctypes.CFUNCTYPE(None)(lambda: common_callback(index, time)))
	return lib.call_after_delay(ctypes.c_float(time), func[-1])

lib = ctypes.cdll.LoadLibrary("/home/pi/robot-framework/callbacks_python/tests/timer_callbacks_test.so")
#lib = ctypes.cdll.LoadLibrary("./timer_callbacks_test.so") #"/usr/local/lib/libpython_callback.so")

n_callbacks = 20

for i in range(n_callbacks):
	timer_launch(float(random.randint(10,1000)/50.0), i, lib)

while int(lib.empty_queue_callback()) == 0:
	print(lib.done_callbacks())
	time.sleep(0.5)

lib.join()
