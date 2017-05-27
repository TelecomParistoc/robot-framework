from ..robot.thread_easy_stop import Thread_Easy_Stop
from ..robot.starting_block import add_jack_and_delay, Wait_Object
from ..local_robot.big_robot import *
from I2C_bus import I2C_bus
from AX12 import AX12
import random
import gpio
import time


def print_ax12_id_on_the_fly(id):
    print "[+] I2C device with ID "+str(id)+" detected"

def callback_catch_print(c):
    try:
        c()
    except Exception as e:
        print "Exception caught : "+str(e)

x = 1
prev_pos_1 = 0
prev_pos_2 = 0
def move_ax12(index, robot, callback):
    global x
    pos = random.randint(0, 512)
    sign = 2*random.randint(0, 1)-1
    if index == 1:
        try:
            print "New position for first ax12 : "+str(min(1023, max(0, prev_pos_1+sign*pos)))
            robot.AX12_first.move(min(1023, max(0, prev_pos_1+sign*pos)), lambda: callback_catch_print(callback))
        except Exception as e:
            print "Exception caught during ax12 moving "+str(e)
    else:
        try:
            print "New position for second ax12 : "+str(min(1023, max(0, prev_pos_2+sign*pos)))
            robot.AX12_second.move(min(1023, max(0, prev_pos_2+sign*pos)), lambda: callback_catch_print(callback))
        except Exception as e:
            print "Exception caught during ax12 moving "+str(e)

def start_seq(index, robot, callback):
    global x
    if index == 1:
        print "Starting sequence 2"
        robot.start_sequence('ax12_2_seq')
    else:
        print "Starting sequence 1"
        robot.start_sequence('ax12_1_seq')
    x += 1
    print x
    callback()


if __name__ == "__main__":

    try:
        I2C_bus.init(115200)
    except Exception as e:
        print "[-] Unable to start I2C communication ("+str(e)+"), exiting"
        exit()

    #scanned = I2C_bus.scan(print_ax12_id_on_the_fly)
    scanned = [129, 145]
    if len(scanned)<2:
        print "[-] Not enough AX12 on I2C bus to achieve the sequence, exiting"
        exit()

    AX12_1 = AX12(scanned[0])
    AX12_2 = AX12(scanned[1])

    gpio.init()

    jack_pin = gpio.gpio_index_of_wpi_pin(5)
    print "Jack pin corresponds to BCM index "+str(jack_pin)

    #gpio.set_pin_mode(jack_pin, gpio.INPUT)
    gpio.set_pin_mode(jack_pin, gpio.OUTPUT) #easier to test with hand (gpio write 5 0 ou 1)

    robot = init()
    robot.add_object(AX12_1, 'AX12_first')
    robot.add_object(AX12_2, 'AX12_second')
    robot.AX12_first.set_torque(400)
    robot.AX12_first.set_speed(100)
    robot.AX12_second.set_torque(400)
    robot.AX12_second.set_speed(100)

    manage_jack = add_jack_and_delay(robot, 10, False)

    gpio.assign_callback_on_gpio_down(24, lambda: manage_jack(False))
    gpio.assign_callback_on_gpio_up(24, lambda: manage_jack(True))


    robot.add_sequence('ax12_1_seq')
    robot.add_parallel((lambda u: move_ax12(1, robot, u), True))
    robot.wait(1)
    robot.add_parallel((lambda u: start_seq(1, robot, u), True))
    robot.wait()
    robot.sequence_done()

    robot.add_sequence('ax12_2_seq')
    robot.add_parallel((lambda u: move_ax12(2, robot, u), True))
    robot.wait(1)
    robot.add_parallel((lambda u: start_seq(2, robot, u), True))
    robot.wait()
    robot.sequence_done()

    robot.wait_sequence() # We wait for jack beeing pushed/pulled
    robot.start_sequence('ax12_1_seq')
    robot.wait_sequence()

    wait_end = Wait_Object()
    wait_end.join()

    robot.stop()
    gpio.join()
