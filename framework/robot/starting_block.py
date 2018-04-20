from thread_easy_stop import Thread_Easy_Stop
import time

from sys import stdout

def time_elapsed(delay, callback):
    def run_step(t):
        if t>delay:
            callback()
            return False
        return True

    thread = Thread_Easy_Stop(callback_in_loop=run_step).start()

def manage_time_elapsed(robot):
    print "[.] End of granted time, stopping robot"
    robot.stop()
    Thread_Easy_Stop.stop_all_threads()



class Wait_Object:

    def __init__(self, callback = None, inter_delay = 0.05):
        self.callback = callback
        self.delay = inter_delay
        self.stopped = False
        self.thread = Thread_Easy_Stop(callback_in_loop = lambda t: self.run_step(t))
        self.thread.start()

    def set_callback(self, callback):
        self.callback = callback

    def run_step(self, t):
        if not self.stopped:
            return True
        else:
            if callable(self.callback):
                self.callback()

            return False

    def stop(self):
        self.stopped = True

    def join(self):
        if self.thread is not None:
            self.thread.join()

    def reset(self):
        if self.stopped:
            self.stopped = False
            self.thread = Thread_Easy_Stop(callback_in_loop = lambda t: self.run_step(t))
            self.thread.start()

class ManageJack:

    def start(self):
        print "[++++] Jack pulled! Actionning robot"
        self.robot.start()

    def abort(self):
        print "[----] Stopping robot because of jack"
        self.robot.stop()

    def __init__(self, robot):
        self.transitions = {'waiting':{'push':('ready', None)},
                            'ready':{'pull':('started', self.start)},
                            'started':{'push':('abort', self.abort)}}

        self.cur_state = 'waiting'

        self.robot = robot

    def manage_event(self, pulled):
        if pulled:
            key = 'pull'
            print "[+] Jack inserted! Waiting for the jack to be pulled"
        else:
            key = 'push'
            print "[+] Jack pulled!"

        if self.cur_state not in self.transitions:
            print "[-] Inexisting transition for state "+self.cur_state
            return

        if key in self.transitions[self.cur_state]:
            self.cur_state, callback = self.transitions[self.cur_state][key]

            if callback is not None:
                callback()


def add_jack_and_delay(robot, delay, start_waiting_jack = True):
    robot.add_object(ManageJack(robot), 'jack')

    time_elapsed(delay, lambda: manage_time_elapsed(robot))

    wait_object = Wait_Object()
    robot.add_method(lambda self: wait_object.stop(), 'start')

    robot.add_sequence('loop_before_start')
    
    #instead of
    #robot.add_parallel((lambda u: wait_object.set_callback(callback=u), True))
    #with the new syntax we write now
    robot.add_parallel(wait_object.set_callback, [])
    robot.add_parallel(stdout.write, ["[.] Waiting for jack to be inserted...\n"], False)

    robot.wait()
    robot.sequence_done()

    robot.add_method(lambda self: robot.start_sequence('loop_before_start'), 'wait_for_jack_pulled')

    if start_waiting_jack:
        robot.wait_for_jack_pulled()

    return lambda pulled: robot.jack.manage_event(pulled)
