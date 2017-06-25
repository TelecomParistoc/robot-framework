from ..local_robot.big_robot import *
import time


if __name__ == "__main__":

    #to replace by move of moving_interface
    def move(robot, x, y, t):
        print "[!!] Moving from "+str(x)+" to "+str(y)+" during "+str(t)
        time.sleep(t)
        robot.receive_callback()

    def ax12_up():
        print "[!!!] Moving ax12 test"

    robot = init()
    robot.AX12_pinces1.move_to((100, 20))                         #no callback => impossible to wait the end of the action
    robot.AX12_pinces2.move_to((200, 10), robot.receive_callback) #callback specified => now robot is able to wait for the end of a number of actions we specify
    robot.wait(10, 1)                                             #robot waits for 1 callback during a maximum delay of 10s
    #robot.wait_sequence(until_the_end=True, wait_until_the_end_of_root_sequence=True)

    robot.add_sequence('first_seq')                                     #A sequence associated with a key is a set of actions that are not executed immediately but stored
    robot.add_parallel((lambda: move(robot, x=10, y=200, t=5), True))   #we specify the fact first function will call the receive_callback from robot object with the second member "True" of the pair
    robot.add_parallel((ax12_up, False))                                #simple action with no callback
    robot.wait()                                                        #by default robot waits receiving all callbacks during an infinite amount of time
    robot.add_parallel((lambda: robot.AX12_pinces1.move_to((250, 20), robot.receive_callback), True))
    robot.add_parallel((lambda: move(robot, x=30, y=250, t=1), True))
    robot.add_parallel((lambda: robot.useless(), False))                #function that is declared in big_robot.py and added to robot during init in big_robot.py
    robot.wait(max_delay=20)
    robot.add_parallel((lambda: robot.move_to((60, 500)), False))       #function that is declared in moving_interface.py and added to robot during init in big_robot.py
    robot.add_parallel((lambda: robot.open_AX12_pinces(), False))       #function that is declared in big_robot.py and added to robot during init in big_robot.py
    robot.wait(5, 1)                                                    #robot waits for 1 callback (will voluntarily not be reached) during a maximum delay of 5s
    robot.sequence_done()                                               #this indicates the end of current sequence and reset


    #We can also execute sequence directly when we are not in a key associated sequence
    robot.add_parallel((ax12_up, False))
    robot.add_parallel((lambda: move(robot, x=-30, y=250, t=4), True))
    robot.wait(5)

    robot.start_sequence('first_seq')                           #launching sequence
    robot.wait_sequence()                                       #waiting until the end of current sequence
    robot.start_last_used(step=1)                               #restarts the last used sequence at step 2 (numbering starts with 1)
    robot.pause()                                               #pausing a sequence is the only way not to get out of current sequence
    time.sleep(6)
    robot.unpause()                                             #sequence continues where it was paused

    robot.add_parallel((lambda: move(robot, x=99999, y=99999, t=8), True))

    robot.wait_sequence(wait_until_the_end_of_root_sequence=True)
    robot.stop()
