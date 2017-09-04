from ..robot.thread_easy_stop import Thread_Easy_Stop
from ..robot.starting_block import add_jack_and_delay
from ..local_robot.big_robot import *
from I2C_bus import I2C_bus
from AX12 import AX12
import gpio
import time


def print_ax12_id_on_the_fly(id):
    print "[+] I2C device with ID "+str(id)+" detected"

x = 1
def move_ax12(index, robot, callback):
    global x
    if index == 1:
        robot.AX12_first.set_torque(100)
        robot.AX12_first.set_speed(10)
        robot.AX12_first.move(10*x, callback)
    else:
        robot.AX12_second.set_torque(100)
        robot.AX12_second.set_speed(10)
        robot.AX12_second.move(10*x, callback)

def start_seq(index, robot, callback):
    global x
    if index == 1:
        robot.start_sequence('ax12_2_seq')
    else:
        robot.start_sequence('ax12_1_seq')
    x += 1
    callback()


if __name__ == "__main__":

    try:
        I2C_bus.init()
    except:
        print "[-] Unable to start I2C communication, exiting"
        exit()

    scanned = I2C_bus.scan(print_ax12_id_on_the_fly)
    if len(scanned)<2:
        print "[-] Not enough AX12 on I2C bus to achieve the sequence, exiting"
        exit()

    AX12_1 = AX12(scanned[0])
    AX12_2 = AX12(scanned[1])

    gpio.init()

    jack_pin = gpio.gpio_index_of_wpi_pin(5)
    print "Jack pin corresponds to BCM index "+str(jack_pin)

    gpio.set_pin_mode(jack_pin, gpio.INPUT)

    robot = init()
    robot.add_object(AX12_1, 'AX12_first')
    robot.add_object(AX12_2, 'AX12_second')

    manage_jack = add_jack_and_delay(robot, 100)

    gpio.assign_callback_on_gpio_down(24, lambda: manage_jack(False))
    gpio.assign_callback_on_gpio_up(24, lambda: manage_jack(True))


    robot.add_sequence('ax12_1_seq')
    robot.add_parallel((lambda u: move_ax12(1, robot, u), True))
    robot.wait()
    robot.add_parallel((lambda u: start_seq(1, robot, u), True))
    robot.sequence_done()

    robot.add_sequence('ax12_2_seq')
    robot.add_parallel((lambda u: move_ax12(2, robot, u), True))
    robot.wait()
    robot.add_parallel((lambda u: start_seq(2, robot, u), True))
    robot.sequence_done()

    robot.wait_sequence() # We wait for jack beeing pushed/pulled
    robot.start_sequence('ax12_1_seq')
    robot.wait_sequence()

    robot.stop()
    gpio.join()
    Thread_Easy_Stop.stop_all_threads()
