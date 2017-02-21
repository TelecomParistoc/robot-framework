from ..local_robot.big_robot import *
from threading import Thread
import time

from sys import argv

if __name__ == "__main__":

    def move(robot, x, y, t, callback=None):
        print "[!!] Moving from "+str(x)+" to "+str(y)+" during "+str(t)

        thread = Thread(target=lambda: run(t,callback)).start()

    def run(t,c):
        time.sleep(t)
        if c is not None:
            c()

    def ax12_up():
        print "[!!!] Moving ax12 test"


    robot = init()
	
    robot.AX12_pinces1.move_to((100, 20))                          #no callback => impossible to wait the end of the action
    robot.AX12_pinces2.move_to((200, 10), robot.create_callback()) #callback specified => now robot is able to wait for the end of a number of actions we specify
    robot.wait(10, 1)                                              #robot waits for 1 callback during a maximum delay of 10s

    robot.add_sequence('first_seq')                                                   #A sequence associated with a key is a set of actions that are not executed immediately but stored
    robot.add_parallel((lambda u: move(robot, x=10, y=200, t=3, callback=u), True))   #we specify the fact first function will call the receive_callback from robot object with the second member "True" of the pair
    robot.add_parallel((ax12_up, False))                                              #simple action with no callback
    robot.wait()                                                                      #by default robot waits receiving all callbacks during an infinite amount of time
    robot.add_parallel((lambda u: robot.AX12_pinces1.move_to((250, 20), u), True))
    robot.add_parallel((lambda u: move(robot, x=30, y=250, t=1, callback=u), True))
    robot.add_parallel((lambda: robot.useless(), False))                #function that is declared in big_robot.py and added to robot during init in big_robot.py
    robot.wait(max_delay=20)
    robot.add_parallel((lambda: robot.move_to((60, 500)), False))       #function that is declared in moving_interface.py and added to robot during init in big_robot.py
    robot.add_parallel((lambda: robot.open_AX12_pinces(), False))       #function that is declared in big_robot.py and added to robot during init in big_robot.py
    robot.wait(4, 1)                                                    #robot waits for 1 callback (will voluntarily not be reached) during a maximum delay of 5s
    robot.sequence_done()                                               #this indicates the end of current sequence and reset


    #We can also execute sequence directly when we are not in a key associated sequence
    robot.add_parallel((ax12_up, False))
    robot.add_parallel((lambda u: move(robot, x=-30, y=250, t=4, callback=u), True))
    robot.wait(5)

    robot.start_sequence('first_seq')                           #launching sequence
    robot.wait_sequence()                                       #waiting until the end of current sequence
    robot.start_last_used(step=1)                               #restarts the last used sequence at step 2 (numbering starts with 1)
    robot.pause()                                               #pausing a sequence is the only way not to get out of current sequence
    time.sleep(5)
    robot.unpause()                                             #sequence continues where it was paused

    robot.add_parallel((lambda u: move(robot, x=99999, y=99999, t=4, callback=u), True))     #adding a 8s duration callback ...
    robot.wait(3)                                                                             #... but waiting only 3s and erasing expected callbacks

    robot.add_parallel((lambda u: move(robot, x=666, y=666, t=7, callback=u), True))         #adding now a 7s duration callback
    robot.wait_sequence(True, True)                                                          #waiting to the end, verifying if previous callback is indeed called but not used
    robot.stop()
