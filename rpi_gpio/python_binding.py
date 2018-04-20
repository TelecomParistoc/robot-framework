# -*- coding: utf-8 -*-


import ctypes
from encapsulate_callback import encapsulate_callback

lib_gpio = ctypes.cdll.LoadLibrary(LIBNAME)

lib_gpio.wpi_to_gpio.restype    = ctypes.c_int
lib_gpio.set_pin_mode.restype   = None
lib_gpio.set_pull_up_down.restype=None
lib_gpio.pin_state.restype      = ctypes.c_int
lib_gpio.set_pin_state.restype  = None
lib_gpio.analog_read.restype    = ctypes.c_int
lib_gpio.analog_write.restype = None
lib_gpio.pwm_write.restype = None

lib_gpio.assign_callback_on_gpio_change.restype = None
lib_gpio.assign_callback_on_gpio_down.restype = None
lib_gpio.assign_callback_on_gpio_up.restype = None

lib_gpio.remove_callbacks_on_gpio_change.restype = None
lib_gpio.remove_callbacks_on_gpio_down.restype = None
lib_gpio.remove_callbacks_on_gpio_up.restype = None
lib_gpio.remove_callbacks_on_gpio.restype = None
lib_gpio.remove_all_callback.restype = None

lib_gpio.init.restype = None
lib_gpio.join.restype = None

INPUT = 0
OUTPUT = 1
PWM_OUTPUT = 2
modes = [INPUT, OUTPUT, PWM_OUTPUT]

NO_PULL_UP_DOWN = 0
PULL_DOWN = 1
PULL_UP = 2
pull_up_down_modes = [NO_PULL_UP_DOWN, PULL_DOWN, PULL_UP]


def gpio_index_of_wpi_pin(index):
    assert (isinstance(index, int))
    return int(lib_gpio.wpi_to_gpio(ctypes.c_int(index)))


def set_pin_mode(id, mode):
    assert (isinstance(id, int))
    assert (mode in modes)

    lib_gpio.set_pin_mode(ctypes.c_int(id), ctypes.c_int(mode))

def set_pull_up_down(id, mode):
    assert (isinstance(id, int))
    assert (mode in pull_up_down_modes)

    lib_gpio.set_pull_up_down(ctypes.c_int(id), ctypes.c_int(mode))

def digital_read(id):
    assert (isinstance(id, int))
    return int(lib_gpio.pin_state(ctypes.c_int(id)))

def digital_write(id, val):
    assert (isinstance(id, int))
    assert (isinstance(val, int))

    lib_gpio.set_pin_state(ctypes.c_int(id), ctypes.c_int(val))

def analog_read(id):
    assert (isinstance(id, int))
    return int(lib_gpio.analog_read(ctypes.c_int(id)))

def analog_write(id, val):
    assert (isinstance(id, int))
    assert (isinstance(val, int))

    lib_gpio.analog_write(ctypes.c_int(id), ctypes.c_int(val))

def pwm_write(id, val):
    assert (isinstance(id, int))
    assert (isinstance(val, int))

    lib_gpio.pwm_write(ctypes.c_int(id), ctypes.c_int(val))


def assign_callback_on_gpio_change(id, callback, one_shot = False):
    assert (isinstance(id, int))
    assert (callable(callback))
    assert (isinstance(one_shot, bool))

    lib_gpio.assign_callback_on_gpio_change(ctypes.c_int(id), encapsulate_callback(callback), ctypes.c_bool(one_shot))

def assign_callback_on_gpio_down(id, callback, one_shot = False):
    assert (isinstance(id, int))
    assert (callable(callback))
    assert (isinstance(one_shot, bool))

    lib_gpio.assign_callback_on_gpio_down(ctypes.c_int(id), encapsulate_callback(callback), ctypes.c_bool(one_shot))

def assign_callback_on_gpio_up(id, callback, one_shot = False):
    assert (isinstance(id, int))
    assert (callable(callback))
    assert (isinstance(one_shot, bool))

    lib_gpio.assign_callback_on_gpio_up(ctypes.c_int(id), encapsulate_callback(callback), ctypes.c_bool(one_shot))


def remove_callbacks_on_gpio_change(id):
    assert (isinstance(id, int))

    lib_gpio.remove_callbacks_on_gpio_change(ctypes.c_int(id))

def remove_callbacks_on_gpio_down(id):
    assert (isinstance(id, int))

    lib_gpio.remove_callbacks_on_gpio_down(ctypes.c_int(id))

def remove_callbacks_on_gpio_up(id):
    assert (isinstance(id, int))

    lib_gpio.remove_callbacks_on_gpio_up(ctypes.c_int(id))

def remove_callbacks_on_gpio(id):
    assert (isinstance(id, int))

    lib_gpio.remove_callbacks_on_gpio(ctypes.c_int(id))

def remove_all_callback():
    lib_gpio.remove_all_callback(ctypes.c_int(id))


def init():
    lib_gpio.init()

def join():
    lib_gpio.join()
