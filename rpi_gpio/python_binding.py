# -*- coding: utf-8 -*-


import ctypes
from encapsulate_callback import *

lib_gpio = ctypes.cdll.LoadLibrary(open("lib_path").read().split('\n')[0])


int pin_state(int id);
void set_pin_state(int id, int state);

void assign_callback_on_gpio_change(int id, c_fct_ptr callback, bool one_shot = false);
void assign_callback_on_gpio_down(int id, c_fct_ptr callback, bool one_shot = false);
void assign_callback_on_gpio_up(int id, c_fct_ptr callback, bool one_shot = false);

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


def check_uint8(x):
    assert (isinstance(x, int))
    assert (0 <= identifiant <= 255)


def check_mode(m):
    assert (m in [DEFAULT_MODE, WHEEL_MODE])


def init_AX12(baudrate):
    assert(isinstance(baudrate, int))
    assert (7343 <= baudrate <= 1000000)

    return int(lib_ax12.initAX12(ctypes.c_int(baudrate)))



def AX12_get_position(identifiant):
    check_uint8(identifiant)
    return float(lib_ax12.AX12getPosition(ctypes.c_uint8(identifiant)))


def AX12_get_speed(identifiant):
    check_uint8(identifiant)
    return float(lib_ax12.AX12getSpeed(ctypes.c_uint8(identifiant)))


def AX12_get_load(identifiant):
    check_uint8(identifiant)
    return float(lib_ax12.AX12getLoad(ctypes.c_uint8(identifiant)))


def AX12_get_status(identifiant):
    check_uint8(identifiant)
    return int(lib_ax12.AX12getStatus(ctypes.c_uint8(identifiant)))


def AX12_get_voltage(identifiant):
    check_uint8(identifiant)
    return float(lib_ax12.AX12getVoltage(ctypes.c_uint8(identifiant)))


def AX12_get_temperature(identifiant):
    check_uint8(identifiant)
    return int(lib_ax12.AX12getTemperature(ctypes.c_uint8(identifiant)))


def AX12_is_moving(identifiant):
    check_uint8(identifiant)
    return int(lib_ax12.AX12isMoving(ctypes.c_uint8(identifiant)))


def AX12_set_mode(identifiant, mode):
    check_uint8(identifiant)
    check_mode(mode)
    return int(lib_ax12.AX12setMode(ctypes.c_uint8(identifiant),
                                    ctypes.c_int(mode)))


def AX12_set_speed(identifiant, speed):
    check_uint8(identifiant)
    return int(lib_ax12.AX12setSpeed(ctypes.c_uint8(identifiant),
                                     ctypes.c_double(speed)))


def AX12_set_torque(identifiant, torque):
    check_uint8(identifiant)
    return int(lib_ax12.AX12setTorque(ctypes.c_uint8(identifiant),
                                      ctypes.c_double(torque)))


def AX12_set_LED(identifiant, state):
    assert(isinstance(state, int))

    return int(lib_ax12.AX12setLED(ctypes.c_uint8(identifiant),
                                   ctypes.c_int(state)))

def encapsulate_callback(callback):
    counter += 1
    lambda_remove_ref = lambda: callback(); del mapped_callbacks[counter]
    mapped_callbacks[counter] = ctypes.CFUNCTYPE(None)(lambda_remove_ref)
    return mapped_callbacks[counter]

def AX12_move(identifiant, position, callback):
    check_uint8(identifiant)
    assert(isinstance(position, float))
    assert(callable(callback))

    return int(lib_ax12.AX12move(ctypes.c_uint8(identifiant), ctypes.c_double(position), encapsulate_callback(callback)))
