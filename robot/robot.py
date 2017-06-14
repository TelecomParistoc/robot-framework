class Robot:

    def add_object(self, obj):

    def add_method(self, method):

    def add_methods_of_object(self, obj):

    def add_sequence(self, name):

    def sequence_done(self):

    def add_parallel(self, to_call_and_is_callback):

    def start_sequence(self, name):

    def wait(self, max_delay=-1):

    def start_last_used(self, step=1):

    def pause(self):

    def unpause(self):

robot.add_parallel((lambda: robot.AX12_pinces1.move_to((250, 20), robot.receive_callback), True))
robot.add_parallel((lambda: move(robot, x=30, y=250, t=5), True))
robot.add_parallel((lambda: robot.useless(), False))                #function that is declared in big_robot.py and added to robot during init in big_robot.py
robot.wait(max_delay=20)
robot.add_parallel((lambda: robot.move_to((60, 500)), False))       #function that is declared in moving_interface.py and added to robot during init in big_robot.py
robot.add_parallel((lambda: robot.open_AX12_pinces()))              #function that is declared in big_robot.py and added to robot during init in big_robot.py
robot.sequence_done()                                               #this indicates the end of current sequence and reset


#We can also execute sequence directly when we are not in a key associated sequence
robot.add_parallel((ax12_up, False))
robot.add_parallel(((lambda: move(robot, x=-30, y=250, t=4), True))
robot.wait()

robot.start_sequence('first_seq')                           #launching sequence
robot.wait()
robot.start_last_used(step=2)                               #restarts the last used sequence at step 2 (numbering starts with 1)
time.sleep(1)
robot.pause()                                               #pausing a sequence is the only way not to get out of current sequence
robot.unpause()                                             #sequence continues where it was paused

robot.wait()
