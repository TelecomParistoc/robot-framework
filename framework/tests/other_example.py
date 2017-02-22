#import the library

from robot import Robot
from AX12 import AX12


# ---------------------------   ROBOT CONSTRUCTION   --------------------------#
#creates the robot skeleton
r = Robot()

#adds motors to the robot skeleton
r.add_object(AX12(141), "motor_1")
r.add_object(AX12(130), "motor_2")


# -------------------------   SEQUENCE DEFINITION ----------------------------#

#defines a sequence of actions
#note that the sequence is only defined and not run (for the moment)
r.add_sequence("seq_1")

#first block of actions; all actions of a block are performed simultaneously
r.add_parallel(r.motor_1.move, [100])
r.add_parallel(r.motor_2.move, [150])
#the "wait" defines the end of the block
#and it waits :
# 	until max_delay seconds are elapsed
# 	OR until n_callbacks actions of this block are done
r.wait(max_delay=3, n_callbacks=2)


#second block of actions; this block will be run AFTER the first one
r.add_parallel(r.motor_1.move, [0])
r.add_parallel(r.motor_2.set_mode, [1], count_enable=False)
r.add_parallel(r.motor_2.set_speed, [50], False)
r.wait(max_delay=5, n_callbacks=1)

r.wait(max_delay=3, n_callbacks=2)
r.add_parallel(r.motor_2.set_mode, [0], count_enable=False)
r.wait(max_delay=1)


#you MUST specify where the definition of the sequence ends
# so the following line means "end of seq_1 definition"
r.sequence_done()



# --------------------- RUNNING ! ------------------------------------------#

# We run the sequence we defined above
r.start_sequence("seq_1")


# We wait the end of the sequence execution
r.wait_sequence()

#close the thread
r.stop()
