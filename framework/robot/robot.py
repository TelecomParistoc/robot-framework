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

            #variables for move
            self.goal_dist = []
            self.move_callback = []
            self.load_moving_interface()

            self.turning = False
            self.turn_callback = []

            self.obstacle_stop = False

        else:
            self.moving_interface = False

    def load_moving_interface(self):
        """
        loads functions from motion.py and motordriver.py
        so we can write for instance robot.moveTo(...)
        It must be called by __init__
        """
        if not self.moving_interface:
            print("[-] Error: moving_interface is set to False; No functions are loaded")
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
        motion.move(1)

    def resume_motion(self):
        self.obstacle_stop = False
        self.time_offset += time.time() - self.frozen_time
        if self.x_dest_stack and self.y_dest_stack and self.final_heading_stack:
            self.moveTo(self.x_dest_stack.pop(), self.y_dest_stack.pop(), \
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
        command sent to MotorController. It's useful to resume the command
        after an emergency stop

        If erase is set to True, all previous orders are forgotten
        Otherwise, order is piled on a stack, so previous orders
        will be executed afterwards
        """
        if not self.moving_interface:
            print("[-] Error in Robot.moveTo; moving_interface is not enabled")
            return

        if self.obstacle_stop:
            self.moveTo_callback_stack = [callback] + self.moveTo_callback_stack
            self.x_dest_stack = [x_dest] + self.x_dest_stack
            self.y_dest_stack = [y_dest] + self.y_dest_stack
            self.final_heading_stack = [final_heading] + self.final_heading_stack
            return

        if self.debug:
            print("[moveTo Python] from ", self.get_pos_X(), self.get_pos_Y(), "to", x_dest, y_dest, " ; time = ", time.time() - self.t_0)

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
            self.goal_dist.append(goal_dist)
            self.move_callback.append(callback)
        else:
            self.goal_dist.append(goal_dist)
            self.move_callback.append(callback)
        motion.move(goal_dist, self.private_move_callback)

    def private_move_callback(self):
        self.goal_dist.pop()
        tmp = self.move_callback.pop()
        if callable(tmp): tmp()


    def load_add_path(self, filename, max_delay=15):

        if self.debug:
            print("[+] adding path: ", filename)
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
        print("[+] Stopping collision detection")


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
