from action import *
import motion
import motordriver
from I2C_bus import I2C_bus             #from libAX12/pythonBinding
import gpio
from threading import Thread
import sys, traceback
from robot import Robot

try:
    I2C_bus.init(115200)
except Exception as e:
    print("[-] Unable to start I2C communication (", str(e), "), exiting")
    exit()

gpio.init()

robot = Robot()

robot.setPosition(500, 500)
robot.set_heading(0)

main = Sequence("main")
main.add_actions([MoveToAction(robot, 700, 500).wait(),
                  MoveToAction(robot, 700, 700).wait()])
main.wait().exec()
