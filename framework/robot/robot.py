from threading import Thread, Lock
import types
import time
import math


import json
from os import listdir
import os
import signal

import motion
import motordriver
import collision_detection

class Robot:
    """
	represents a robot on which we can add objects (like AX12 motors for example)
	or specify sequences of actions
    """

    def __init__(self, debug=True, moving_interface=True):
	"""
	    Constructs a new Robot object, and launch the sequence thread
	"""

        self.debug = debug
        self.received_callbacks = 0

        self.cur_sequence = ""
        self.last_sequence = ""
        self.cur_parallel = 0
        self.cur_sequence_constructed = ""
        self.temp_delays = []
        self.temp_sequence = [[]]
        self.temp_expected_callbacks = [0]
        self.delays = {'':[]}
        self.sequences = {'':[[]]}
        self.expected_callbacks = {'':[0]}
        self.sequence_queue = []
        self.sequence_mutex = Lock()
        self.color = None

        self.expected_callback_indexes = []
        self.current_callback_index = 0

        self.t_0 = time.time()
        self.frozen_time = None
        self.time_offset = 0

	self.to_call_at_stop = None

        if moving_interface:
            self.moving_interface = True
            self.actual_path = None

            #variables for moveTo
            self.x_dest_stack = []
            self.y_dest_stack = []
            self.final_heading_stack = []
            self.moveTo_callback_stack = []

            #variables for moveTo when an obstacle is blocking the direct path
            self.x_dest_avoiding_obstacle_stack = []
            self.y_dest_avoiding_obstacle_stack = []
            self.final_heading_avoiding_obstacle_stack = []
            self.moveTo_callback_avoiding_obstacle_stack = []
            
            #variables for move
            self.goal_dist = []
            self.move_callback = []
            self.load_moving_interface()

            self.turning = False
            self.turn_callback = []

            self.obstacle_stop = False

        else:
            self.moving_interface = False

        self.started = False
        self.thread = Thread(target=lambda: self.run()).start()


    def load_moving_interface(self):
        """
            loads functions from motion.py and motordriver.py
            so we can write for instance robot.moveTo(...)
            It must be called by __init__
        """
        if not self.moving_interface:
            print "[-] Error: moving_interface is set to False; No functions are loaded"
            return

        for module in [motion, motordriver]:
            for module_attribute in dir(module):
                attr = getattr(module, module_attribute)
                if callable(attr):

                    #these functions are already overriden, see below
                    if attr.__name__ in ["moveTo", "turn", "move"]:
                        continue

                    #warning: functions in motion or motordriver does not
                    #take robot in first argument
                    #but when we write robot.function(foo), function gets
                    #actually 2 arguments: robot and foo
                    #so here we have to remove the first argument
                    #a more precise adaptation should be done
                    self.add_method((lambda attr_copy: (lambda *args: attr_copy(*args[1:])))(attr),
                                    name=attr.__name__)

    def stop_motion(self):
        self.obstacle_stop = True
        self.frozen_time = time.time()
        if self.getDirection() == motion.DIR_FORWARD:
            motion.move(1)
        else:
            motion.move(-1)

    def resume_motion(self):
	print"[Collision Detection] Restarting movement blocked by obstacle"
        self.obstacle_stop = False
        self.time_offset += time.time() - self.frozen_time
        self.moveTo_callback_avoiding_obstacle_stack = []
        self.x_dest_avoiding_obstacle_stack = []
        self.y_dest_avoiding_obstacle_stack = []
        self.final_heading_avoiding_obstacle_stack = []
        if self.x_dest_stack and self.y_dest_stack and self.final_heading_stack:
            self.moveTo(self.x_dest_stack.pop(), self.y_dest_stack.pop(),
                    self.final_heading_stack.pop(), self.moveTo_callback_stack.pop())

    def turn(self, heading, callback=lambda: None):

        self.turning = True
        self.turn_callback.append(callback)
        motion.turn(heading, callback=self.private_turn_callback)

    def private_turn_callback(self):
        self.turning = False
        self.turn_callback.pop()()

    def set_turning(self, value):
        #value must be True or False
        self.turning = value

    def erase_moveTo_stack(self):
        self.x_dest_stack = []
        self.y_dest_stack = []
        self.final_heading_stack = []

    def moveTo(self, x_dest, y_dest, final_heading=-1, callback=None,
                erase=True):
        """
            this function does the same thing as motion.moveTo, but saves the
            command sent to MotorController. It's usefull to resume the command
            after an emergency stop

            If erase is set to True, all previous orders are forgotten
            Otherwise, order is piled on a stack, so previous orders
            will be executed afterwards
        """
        if not self.moving_interface:
            print "[-] Error in Robot.moveTo; moving_interface is not enable"
            return

        if self.debug:
            print "[moveTo Python] from ", self.get_pos_X(), self.get_pos_Y(), "to", x_dest, y_dest, " ; time = ", time.time() - self.t_0

        if self.obstacle_stop:
            self.temp_expected_callbacks[-1] += 1
            self.moveTo_callback_avoiding_obstacle_stack.append(callback) #The stack is useless in this case, but let's keep it just in case we need a better approach
            self.x_dest_avoiding_obstacle_stack.append(x_dest)
            self.y_dest_avoiding_obstacle_stack.append(y_dest)
            self.final_heading_avoiding_obstacle_stack.append(final_heading)
	    self.turning = True
	    motion.set_after_first_turn_of_move_to_callback(lambda: self.set_turning(False))
	    motion.set_after_translation_of_move_to_callback(lambda: self.set_turning(True))
	    motion.moveTo(x_dest, y_dest, final_heading, self.private_moveTo_callback)
            return

        if erase:
            self.erase_moveTo_stack()

        self.moveTo_callback_stack.append(callback)
        self.x_dest_stack.append(x_dest)
        self.y_dest_stack.append(y_dest)
        self.final_heading_stack.append(final_heading)
        self.turning = True
        motion.set_after_first_turn_of_move_to_callback(lambda: self.set_turning(False))
        motion.set_after_translation_of_move_to_callback(lambda: self.set_turning(True))
        motion.moveTo(x_dest, y_dest, final_heading, self.private_moveTo_callback)

    def private_moveTo_callback(self):

        #It's ugly, but there was no other choice	
        if self.obstacle_stop:
            if self.x_dest_avoiding_obstacle_stack:
	        self.x_dest_avoiding_obstacle_stack.pop()
                self.y_dest_avoiding_obstacle_stack.pop()
                self.final_heading_avoiding_obstacle_stack.pop()
                tmp = self.moveTo_callback_avoiding_obstacle_stack.pop()
                if callable(tmp): tmp()

	    self.turning = False
            #if stacks are not empty
            if self.x_dest_avoiding_obstacle_stack:
                time.sleep(.3)
                motion.moveTo(self.x_dest_avoiding_obstacle_stack[-1], self.y_dest_avoiding_obstacle_stack[-1],
                        self.final_heading_avoiding_obstacle_stack[-1], self.private_moveTo_callback)
	
        if self.x_dest_stack:
	    self.x_dest_stack.pop()
            self.y_dest_stack.pop()
            self.final_heading_stack.pop()
            tmp = self.moveTo_callback_stack.pop()
            if callable(tmp): tmp()

	self.turning = False
        #if stacks are not empty
        if self.x_dest_stack:
            time.sleep(.3)
            motion.moveTo(self.x_dest_stack[-1], self.y_dest_stack[-1],
                        self.final_heading_stack[-1], self.private_moveTo_callback)

    def move(self, goal_dist, callback=None, erase=True):
        """
            same thing as moveTo
        """
        if erase:
            self.goal_dist = []
            self.move_callback = []
            self.goal_dist.append(goal_dist)
            self.move_callback.append(callback)
        else:
            self.goal_dist.append(goal_dist)
            self.move_callback.append(callback)
        motion.move(goal_dist, self.private_move_callback)

    def private_move_callback(self):
        if self.goal_dist:
            self.goal_dist.pop()
            tmp = self.move_callback.pop()
            if callable(tmp): tmp()


    def add_path_to_follow(self, path, max_delay=15):
        """
            defines a list of moveTo to follow a list of points [(x0, y0), (x1, y1), ...]
            These actions are added to the sequence which is currently being defined
            It's not yet executed!
            Don't forget that the orientation at the end of the path is not specified!
        """
        for x, y in path:
            self.add_parallel(self.moveTo, [x, y, -1])
            self.wait(max_delay=max_delay)

    def load_add_path(self, filename, max_delay=15):

        if self.debug:
            print "[+] adding path: " + filename
        path = json_to_python(filename, self.color)
        self.add_path_to_follow(path, max_delay=max_delay)


    def start_collision_detection(self, front_detection, rear_detection):
        """
            front_detection and rear_detection must be 2 functions without
            parameters, which respectively return True if and only if there is
            an obstacle in the forward (backward) direction

            delay is the delay in seconds between two calls to these functions

            when the robot is close from edges, sensors are disabled
            if distance from edge <= no_sensor_distance, then sensors are disabled

            heading_in_y_direction is the heading to have to go in the direction +y

            How to react when a collison is detected is not yet very well defined...
        """
        self.enable_collision_detection = True
        self.collision_thread = Thread(target=collision_detection.sensor_manager,
                                        args=[self, front_detection, rear_detection])
        self.collision_thread.start()


    def stop_collision_sensors(self):
        self.enable_collision_detection = False
        print "[+] Stopping collision detection"


    def add_method(self, func, name=None):
        if name == None:
            if '__name__' not in dir(func):
                print("[-] Unable to retrieve name from function during method adding")
                return
            return setattr(self, func.__name__, types.MethodType(func, self))
        else:
            return setattr(self, name, types.MethodType(func, self))



    @classmethod
    def add_class_method(cls, func, name=None):
        if name == None:
            if '__name__' not in dir(func):
                print("[-] Unable to retrieve name from function during method adding")
                return
            return setattr(cls, func.__name__, types.MethodType(func, cls))
        else:
            return setattr(cls, name, types.MethodType(func, cls))



    def add_object(self, obj, name=None):
        if name == None:
            if '__name__' not in dir(obj):
                print("[-] Unable to retrieve name from obj during object adding")
                return
            return setattr(self, obj.__name__, obj)
        else:
            return setattr(self, name, obj)



    def add_methods_of_object(self, obj):
        for f,attr in [(method, getattr(obj, method)) for method in dir(obj) if not method.startswith('_')]:
            if hasattr(attr, '__call__'):
                self.add_method(attr, method)



    def add_sequence(self, name):
        self.sequence_mutex.acquire()

        if name is None or name == "":
            print("[-] Name of sequence must not be empty, no sequence added")
            self.sequence_mutex.release()
            return False
        elif self.cur_sequence_constructed != "":
            print("[-] There must not be a current sequence filled, no sequence added")
            self.sequence_mutex.release()
            return False

        self.sequences[name] = []
        self.temp_delays = []
        self.temp_sequence = [[]]
        self.temp_expected_callbacks = [0]
        self.cur_sequence_constructed = name

        if self.debug:
            print("[+] New sequence added with name "+self.cur_sequence_constructed+"; now fill it")

        self.sequence_mutex.release()
        return True



    def sequence_done(self):
        self.sequence_mutex.acquire()

        if self.cur_sequence_constructed == "":
            print("[-] Root sequence could never be done")
            self.sequence_mutex.release()
            return False

        if len(self.temp_delays) < len(self.temp_sequence):
            self.temp_delays.append(-1.0)
            if len(self.temp_delays) != len(self.temp_sequence):
                print("[-] Strange thing detected, should not happen (delays table must have the same length as sequence table). Contact admin")
                self.sequence_mutex.release()
                return False

        self.delays[self.cur_sequence_constructed] = self.temp_delays
        self.sequences[self.cur_sequence_constructed] = self.temp_sequence
        self.expected_callbacks[self.cur_sequence_constructed] = self.temp_expected_callbacks
        if self.debug:
            print("[+] New sequence "+self.cur_sequence_constructed+" has been completed, it is made of "+str(len(self.temp_sequence))+" parts")

        self.cur_sequence_constructed = ""
        self.temp_delays = []
        self.temp_sequence = [[]]
        self.temp_expected_callbacks = [0]

        self.sequence_mutex.release()

        self.list_parallel_threads = []
        return True

    def add_parallel_thread(self, function, arg_list, count_enable=True, force_root_seq=False):
        """
            same as add_parallel but function is launched in a separated Thread
        """

        def to_be_added(*args):
            t = Thread(target=function, args=args)
            self.list_parallel_threads.append(t)
            t.start()

        self.add_parallel(
            lambda *args: to_be_added(*args), arg_list,
                    count_enable=count_enable, force_root_seq=force_root_seq)

    def add_parallel(self, function, arg_list, count_enable=True, force_root_seq=False):
    	if not (isinstance(arg_list, tuple) or isinstance(arg_list, list)):
    	    raise(TypeError("parameter arg_list must be a list or a tuple"))

    	if count_enable:
    	    return self.private_add_parallel((lambda u: function(*(arg_list + [u])), True),
    					force_root_seq=force_root_seq)
    	else:
    	    return self.private_add_parallel((lambda: function(*arg_list), False),
    					force_root_seq=force_root_seq)


    def private_add_parallel(self, to_call_and_is_callback, force_root_seq=False):
        self.sequence_mutex.acquire()

        if self.cur_sequence_constructed != "":
            number_parallels = len(self.temp_sequence)-1

            self.temp_sequence[-1].append(to_call_and_is_callback)
            if to_call_and_is_callback[1]:
                self.temp_expected_callbacks[-1] += 1
                if self.debug:
                    print("[.] Function with callback added to current sequence "+self.cur_sequence_constructed+" at step "+str(number_parallels))
            elif self.debug:
                print("[.] Function with no callback added to current sequence "+self.cur_sequence_constructed+" at step "+str(number_parallels))

        elif self.cur_sequence == "" or force_root_seq:
            number_parallels = len(self.sequences[""])

            self.sequences[""][-1].append(to_call_and_is_callback)
            if to_call_and_is_callback[1]:
                self.expected_callbacks[""][-1] += 1
                if self.debug:
                    print("[.] Function with callback added to current root sequence at step "+str(number_parallels))
            elif self.debug:
                print("[.] Function with no callback added to current root sequence at step "+str(number_parallels))

        else:
            if self.debug:
                print("[-] Unable to add parallel to empty sequence constructed if no force root sequence parameter is specified")
            self.sequence_mutex.release()
            return False

        self.sequence_mutex.release()
        return True



    def wait(self, max_delay=-1.0, n_callbacks=-1):
        self.sequence_mutex.acquire()

        if self.cur_sequence_constructed != "":
            self.temp_delays.append(max_delay)
            self.temp_sequence.append([])
            if n_callbacks>=0:
                self.temp_expected_callbacks[-1] = n_callbacks
            self.temp_expected_callbacks.append(0)
            if self.debug:
                print("[++] New step added to current sequence "+self.cur_sequence_constructed+", with a delay of "+str(max_delay))

        else:
            if len(self.sequences[""][-1]) == 0:
                if n_callbacks>=0:
                    self.delays[""].append(max_delay)
                    self.sequences[""].append([])
                    self.expected_callbacks[""][-1] = n_callbacks
                    self.expected_callbacks[""].append(0)
                    if self.debug:
                        print("[+] Waiting aimlessly "+str(max_delay)+"s until receiving "+str(n_callbacks)+" callbacks")
                elif self.debug:
                    print("[-] Useless wait because no action in queue, no wait added")
                    self.sequence_mutex.release()
                    return False
            else:
                self.delays[""].append(max_delay)
                self.sequences[""].append([])
                if n_callbacks>=0:
                    self.expected_callbacks[""][-1] = n_callbacks
                self.expected_callbacks[""].append(0)
                if self.debug:
                    print("[++] New step added to current root sequence with a delay of "+str(max_delay))

        self.sequence_mutex.release()
        return True



    def start_sequence(self, name, step=0):
        if not self.started:
            print("[-] Sequence not started because thread is finished, please construct another instance")
            return False

        self.sequence_mutex.acquire()

        if name is None or name == "":
            if self.debug:
                print("[-] Unable to start empty sequence")
            self.sequence_mutex.release()
            return False
        elif step+1>=len(self.sequences[name]):
            if self.debug:
                print("[-] There is not enough steps in sequence "+name+" : step "+str(step)+" is too high")
            self.sequence_mutex.release()
            return False

        if self.cur_sequence == "" and len(self.sequences[""]) <= 1 and len(self.sequences[""][-1]) == 0:
            self.cur_sequence = name
            self.last_sequence = name
            self.cur_parallel = step
            if self.debug:
                print("[+++] Starting sequence "+self.cur_sequence+" over empty root sequence")
            self.reset_waited_callbacks_release_acquire_launch_sequence()
        elif self.cur_sequence == "":
            if self.debug:
                print("[++] Adding sequence "+name+" to queue (waiting for end of root sequence)")
            self.sequence_queue.append((name, step))
        else:
            if self.debug:
                print("[++] Adding sequence "+name+" to queue (waiting for end of sequence "+self.cur_sequence+")")
            self.sequence_queue.append((name, step))

        self.sequence_mutex.release()

        return True


    def start_last_used(self, step=0):
        if not self.started:
            print("[-] Last sequence not started because thread is finished, please construct another instance")
            return False

        self.sequence_mutex.acquire()

        if self.last_sequence == "":
            if self.debug:
                print("[-] Unable to start empty sequence")
            self.sequence_mutex.release()
            return False
        elif step+1>=len(self.sequences[self.last_sequence]):
            if self.debug:
                print("[-] There is not enough steps in sequence "+self.last_sequence+" : step "+str(step)+" is too high")
            self.sequence_mutex.release()
            return False

        if self.cur_sequence == "" and len(self.sequences[""]) <= 1 and len(self.sequences[""][-1]) == 0:
            self.cur_sequence = self.last_sequence
            self.cur_parallel = step
            if self.debug:
                print("[+++] Starting sequence "+self.last_sequence+" over root sequence at step "+str(step))
            self.reset_waited_callbacks_release_acquire_launch_sequence()
        else:
            if self.debug:
                print("[++] Adding sequence "+self.last_sequence+" at step "+str(step)+" to queue")
            self.sequence_queue.append((self.last_sequence, step))

        self.sequence_mutex.release()

        return True



    def wait_sequence(self, until_the_end=False, wait_until_the_end_of_root_sequence=False):
        self.sequence_mutex.acquire()

        if self.cur_sequence == "":
            wait_until_the_end_of_root_sequence = True

        base = self.cur_sequence

        if self.debug:
            if base == "":
                print("[...] Waiting for root sequence to finish")
            else:
                print("[...] Waiting for sequence "+base+" to finish")
        while (((self.cur_sequence == base and base != "") and not until_the_end) or (self.cur_sequence != '' and until_the_end)) and self.started:
            self.sequence_mutex.release()
            time.sleep(0.01)
            self.sequence_mutex.acquire()

        if self.cur_sequence == "" and wait_until_the_end_of_root_sequence:
            while (self.cur_sequence == "" and (len(self.sequences[""])>1 or len(self.sequences[""][0])>=1)) and self.started:
                self.sequence_mutex.release()
                time.sleep(0.05)
                self.sequence_mutex.acquire()

        if not self.started:
            self.cur_sequence = ""

        if self.debug:
            if base == "":
                if self.cur_sequence == '':
                    print("[+] Root Sequence is finished")
                else:
                    print("[++] Root sequence is finished and "+self.cur_sequence+" started right after")
            else:
                if self.cur_sequence == '':
                    if len(self.sequences[""])>1 or len(self.sequences[""][0])>=1:
                        print("[+] Sequence "+base+" is finished, returning to root sequence")
                    else:
                        print("[+] Sequence "+base+" is finished, and all actions in root sequence are done")
                else:
                    print("[+] Sequence "+base+" is finished, returning to "+self.cur_sequence+" sequence")

        self.sequence_mutex.release()



    def launch_sequence(self, step):
        self.sequence_mutex.acquire()

        for s,c in self.sequences[self.cur_sequence][step]:
            self.sequence_mutex.release()
            if c:
                if s.__code__.co_argcount != 1:
                    if self.debug:
                        print("[-] Unable to execute function waiting for a callback as argument with strictly more or less than 1 argument")
                else:
                    s(self.create_callback())
            else:
                if s.__code__.co_argcount != 0:
                    if self.debug:
                        print("[-] Unable to execute function waiting for strictly non negative number of arguments with 0 argument")
                else:
                    s()

            self.sequence_mutex.acquire()

        self.sequence_mutex.release()


    def create_callback(self):
        self.sequence_mutex.acquire()

        a = self.current_callback_index
        f = lambda: self.receive_callback(a)
        self.expected_callback_indexes.append(self.current_callback_index)
        self.current_callback_index += 1

        self.sequence_mutex.release()

        return f


    def receive_callback(self, index):
        self.sequence_mutex.acquire()

        if not self.obstacle_stop:
            if index in self.expected_callback_indexes:
                self.received_callbacks += 1
                if self.debug:
                    print("[++] One more callback with ID "+str(index)+" received ("+str(self.received_callbacks)+" out of "+str(len(self.expected_callback_indexes))+")")
            elif self.debug:
                print("[-] Callback with ID "+str(index)+" received but it's not an expected callback")

        self.sequence_mutex.release()



    def reset_waited_callbacks_release_acquire_launch_sequence(self, step=0):
        self.expected_callback_indexes = []
        self.sequence_mutex.release()
        self.launch_sequence(step)
        self.sequence_mutex.acquire()



    def pause(self):
        self.paused = True
        if self.debug:
            print("[...] Pausing thread")


    def unpause(self):
        self.paused = False
        if self.debug:
            print("[++] Unpausing thread")

    def custom_timer(self):
        """
            if we are avoiding an obstacle, we want to shift all our actions in
            time.
        """

        if not self.obstacle_stop:
            return time.time() - self.time_offset
        else:
            return self.frozen_time

    def run(self):
	spam_console = True
        self.started = True
        self.paused = False
        prev_time = self.custom_timer()
        print("[+++] Starting sequence thread")
        while self.started:
            if not self.paused:
                self.sequence_mutex.acquire()

                #print(self.cur_sequence, self.cur_parallel, self.sequences[self.cur_sequence], self.delays[self.cur_sequence], self.expected_callbacks[self.cur_sequence], self.sequence_queue)
                if self.cur_sequence == "" and len(self.sequences[""]) <= 1 and len(self.sequences[""][0]) == 0:
                    if spam_console:
		        print("[...] No action in root sequence, doing nothing")
		        spam_console = False
                else:
		    spam_console = True
                    deltime = self.custom_timer()-prev_time
                    #print self.cur_sequence, self.cur_parallel, len(self.delays), len(self.delays[self.cur_sequence]), self.received_callbacks, self.expected_callbacks[self.cur_sequence]
                    if (self.delays[self.cur_sequence][self.cur_parallel]>0 and deltime>self.delays[self.cur_sequence][self.cur_parallel]) or self.received_callbacks >= self.expected_callbacks[self.cur_sequence][self.cur_parallel]:
                        if self.cur_sequence == "":
                            if self.cur_parallel != 0 and self.debug:
                                print("[-] Cur parallel is not null whereas we are in root sequence, should not happen")

                            if len(self.sequences[""])<=1 and len(self.sequences[""][0]) == 0:
                                if len(self.sequence_queue)>0:
                                    if self.debug:
                                        print("[++] All actions of root sequence has been done, queue is not empty, popping sequence "+self.sequence_queue[0][0]+" at step "+str(self.sequence_queue[0][1]))
                                elif self.debug:
                                    print("[+++] All actions of root sequence has been done, no more actions")

                            self.cur_parallel = 0
                            self.received_callbacks = 0
                            prev_time = self.custom_timer()

                            if len(self.sequences[""])>=1:
                                del self.sequences[""][0]
                                del self.delays[""][0]
                                del self.expected_callbacks[""][0]

                                if len(self.sequences[""])>1:
                                    self.reset_waited_callbacks_release_acquire_launch_sequence()
                                else:
                                    if len(self.sequence_queue)>0:
                                        self.cur_sequence, self.cur_parallel = self.sequence_queue[0]
                                        self.last_sequence = self.cur_sequence
                                        del self.sequence_queue[0]
                                        self.reset_waited_callbacks_release_acquire_launch_sequence()
                                    else:
                                        if len(self.delays[""]) == 0:
                                            self.delays[""].append(-1)
                                        if len(self.sequences[""])>0:
                                            self.reset_waited_callbacks_release_acquire_launch_sequence()
                            if len(self.sequences[""]) == 0:
                                self.sequences[""] = [[]]
                                self.expected_callbacks[""] = [0]

                        else:
                            self.cur_parallel += 1
                            self.received_callbacks = 0
                            prev = self.cur_sequence
                            if self.cur_parallel+1 >= len(self.delays[self.cur_sequence]):
                                prev_parallel = self.cur_parallel
                                if len(self.sequence_queue)>0:
                                    seq = self.sequence_queue[0]
                                    self.cur_sequence, self.cur_parallel = seq
                                    seq = seq[0]
                                    del self.sequence_queue[0]
                                    self.last_sequence = self.cur_sequence
                                else:
                                    seq = 'root'
                                    self.cur_sequence = ''

                                self.cur_parallel = 0
                                prev_time = self.custom_timer()
                                self.reset_waited_callbacks_release_acquire_launch_sequence()

                                if self.debug:
                                    print("[+++] Parallel block "+str(prev_parallel)+" done, all actions of sequence "+prev+" has been done, we return to "+seq+" sequence")
                            else:
                                prev_time = self.custom_timer()
                                self.reset_waited_callbacks_release_acquire_launch_sequence(self.cur_parallel)
                                if self.debug:
                                    if self.cur_sequence != "":
                                        print "[+] Parallel block "+str(self.cur_parallel)+" done in sequence "+self.cur_sequence+"; continuing (time stamp =", time.time() - self.t_0, ")"

                self.sequence_mutex.release()

            time.sleep(0.01)
        print("[+++] Sequence thread ended")


    def stop(self):
        self.started = False
        self.stop_collision_sensors()
        if self.moving_interface:
            self.emergency_stop()
        if self.debug:
            print("[++][...] Stopping sequence thread")
	
	if callable(self.to_call_at_stop):
	    self.to_call_at_stop()
        time.sleep(.2) #make sure previous orders have been sent

        os.kill(os.getpid(), signal.SIGKILL)

    def is_running(self):
        return self.started

######### Paths ########

def json_to_python(filename, color):
    """
        loads a .json and returns a list [(x0, y0), (x1, y1), ...]
        make sure color is "green" or "orange"
    """
    with open(filename, "r") as f:
        result = json.loads(f.read())

    return  [(p['x'], p['y']) for p in result[color][0]['points']]


def load_all_path(color):
    assert color == "green" or color == "orange"

    for file in listdir(PATHS_FOLDER):
        exec("global " + file + " = json_to_python(file, color)")
