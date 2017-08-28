# -*- coding: utf-8 -*-


import ctypes
from encapsulate_callback import encapsulate_callback

lib_gpio = ctypes.cdll.LoadLibrary(open("lib_path").read().split('\n')[0])



void remove_callbacks_on_gpio_change(int id);
void remove_callbacks_on_gpio_down(int id);
void remove_callbacks_on_gpio_up(int id);
void remove_callbacks_on_gpio(int id);
void remove_all_callback();

void join();




def get_pin_state(id):
    assert (isinstance(id, int))

    return int(lib_gpio.pin_state(ctypes.c_int(id)))

def set_pin_state(id, val):
    assert (isinstance(id, int))
    assert (isinstance(val, int))

    lib_gpio.set_pin_state(ctypes.c_int(id), ctypes.c_int(val))


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

def join():
    lib_gpio.join()
