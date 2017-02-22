from robot import Robot		#robot is an installed package

#from utils import AX12, moving_interface  #This part is temporary : AX12 and Moving_Interface will be packages in a near future

#this file should import moving_interface, but moving_interface is not yet implemented !!
#from utils import moving_interface 	#This line is temporary
from AX12 import AX12			#This part isn't


def open_AX12_pinces(r):
    r.AX12_pinces1.move_to((15, 300))
    r.AX12_pinces2.move_to((85, 70))


def useless_function(robot):
    print "[!!] Insert your useless sentence here"


def init():
    robot_skeleton = Robot()
    
    robot_skeleton.add_object(AX12(161), 'AX12_pinces1')
    robot_skeleton.add_object(AX12(130), 'AX12_pinces2')
    robot_skeleton.add_methods_of_object(moving_interface)
    robot_skeleton.add_method(open_AX12_pinces, 'open_AX12_pinces')
    robot_skeleton.add_method(useless_function, 'useless')

    return robot_skeleton
