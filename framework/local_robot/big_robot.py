from robot import *


robot_skeleton = Robot()

def open_AX12_pinces(r):
    r.AX12_pinces1.move_to((15, 300))
    r.AX12_pinces2.move_to((85, 70))

def useless_function():
    print "Insert your useless sentence here"


def init():
    robot_skeleton.add_object('AX12_pinces1', AX12(125))
    robot_skeleton.add_object('AX12_pinces2', AX12(132))
    robot_skeleton.add_methods_of_object(moving_interface)
    robot_skeleton.add_method_robot_as_argument('open_AX12_pinces', open_AX12_pinces)
    robot_skeleton.add_method('useless', useless_function)

    return robot_skeleton
