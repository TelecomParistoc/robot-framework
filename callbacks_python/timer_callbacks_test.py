#!/usr/bin/python
#coding: utf8


from encapsulate_callback import encapsulate_callback
import random
import ctypes
import time


def common_callback(index, time):
	print "Callback with index "+str(index)+" reached after a "+str(time)+" seconds delay"

def timer_launch(time, index, lib):
	return lib.call_after_delay(ctypes.c_float(time), encapsulate_callback(lambda: common_callback(index, time), True))

#lib = ctypes.cdll.LoadLibrary("/home/pi/robot-framework/callbacks_python/tests/timer_callbacks_test.so")
lib = ctypes.cdll.LoadLibrary("./timer_callbacks_test.so")

n_callbacks = 20

for i in range(n_callbacks):
	timer_launch(float(random.randint(10,1000)/50.0), i, lib)

while int(lib.empty_queue_callback()) == 0:
	print(lib.done_callbacks())
	time.sleep(0.5)

lib.join()
