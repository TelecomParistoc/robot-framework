from thread_easy_stop import Thread_Easy_Stop
import time


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



class Wait_Object:

    def __init__(self, callback = None, inter_delay = 0.05):
        self.callback = callback
        self.delay = inter_delay
        self.stopped = False
        self.thread = Thread_Easy_Stop(callback_in_loop = lambda t: self.run_step(t)).start()

    def set_callback(self, callback):
        self.callback = callback

    def run_step(self, t):
        if not self.stopped:
            return True
        else:
            print "Callback calling"
            print self.callback
            if callable(self.callback):
                self.callback()

            return False

    def stop(self):
        self.stopped = True

    def join(self):
        print "None ?"
        print self.thread
        if self.thread is not None:
            self.thread.stop()
            self.thread.join()

    def reset(self):
        if self.stopped:
            self.stopped = False
            self.thread = Thread_Easy_Stop(callback_in_loop = lambda t: self.run_step(t)).start()


class manage_jack:

    def start(self):
        print "[++++] Actionning robot"
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
        else:
            key = 'push'

        if self.cur_state not in self.transitions:
            print "[-] Inexisting transition for state "+self.cur_state
            return

        if key in self.transitions[self.cur_state]:
            self.cur_state, callback = self.transitions[self.cur_state][key]
            if callback is not None:
                callback()


def add_jack_and_delay(robot, delay, start_waiting_jack = True):
    robot.add_object(manage_jack(robot), 'jack')

    time_elapsed(delay, lambda: manage_time_elapsed(robot))

    wait_object = Wait_Object()
    robot.add_method(lambda self: wait_object.stop(), 'start')

    robot.add_sequence('loop_before_start')
    robot.add_parallel((lambda u: wait_object.set_callback(callback=u), True))
    robot.wait()
    robot.sequence_done()

    robot.add_method(lambda self: robot.start_sequence('loop_before_start'), 'wait_for_jack_pulled')

    if start_waiting_jack:
        robot.wait_for_jack_pulled()

    return lambda pulled: robot.jack.manage_event(pulled)
