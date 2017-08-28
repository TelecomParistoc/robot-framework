# This file is necessary when trying to interface C code with python callbacks to keep alive objects that hold python callbacks

import ctypes


mapped_callbacks = {}
counter = 0


def call_and_delete(index, callback):
    global mapped_callbacks
    callback()
    del mapped_callbacks[index]

def encapsulate_callback(callback, one_shot=False):
    global mapped_callbacks
    global counter

    counter += 1
    local_index = counter
    if one_shot:
        lambda_remove_ref = lambda: call_and_delete(local_index, callback)
        mapped_callbacks[counter] = ctypes.CFUNCTYPE(None)(lambda_remove_ref)
    else:
        mapped_callbacks[counter] = ctypes.CFUNCTYPE(None)(callback)

    return mapped_callbacks[counter]


def clear_all():
    global mapped_callbacks
    global counter

    del mapped_callbacks
    counter = 0
    mapped_callbacks = {}
