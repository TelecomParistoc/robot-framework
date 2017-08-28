# This file is necessary when trying to interface C code with python callbacks to keep alive objects that hold python callbacks

import ctypes


mapped_callbacks = {}
counter = 0


def encapsulate_callback(callback, one_shot=False):
    global mapped_callbacks
    global counter

    counter += 1
    if one_shot:
        print("Removing counter "+str(counter))
        lambda_remove_ref = lambda: callback(); del mapped_callbacks[counter]
        mapped_callbacks[counter] = ctypes.CFUNCTYPE(None)(lambda_remove_ref)
    else:
        mapped_callbacks[counter] = ctypes.CFUNCTYPE(None)(callback)
    print(mapped_callbacks[counter])
    return mapped_callbacks[counter]


def clear_all():
    global mapped_callbacks
    global counter

    del mapped_callbacks
    counter = 0
    mapped_callbacks = {}
