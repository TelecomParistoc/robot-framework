from threading import Thread
import time


def time_elapsed(delay, callback):
    def run():
        time.sleep(delay)
        callback()

    thread = Thread(target=run).start()

def manage_time_elapsed(robot):
    print "[.] End of granted time, stopping robot"
    robot.stop()



class Wait_Object:

    def __init__(self, callback = None, inter_delay = 0.05):
        self.callback = callback
        self.delay = inter_delay
        self.stop = False
        self.ended = False
        self.thread = Thread(target=self.run).start()

    def set_callback(self, callback):
        self.callback = callback

    def run(self):
        while not self.stop:
            time.sleep(self.delay)
        if callable(self.callback):
            self.callback()
        self.ended = True

    def stop(self):
        self.stop = True

    def join(self):
        while not self.ended:
            time.sleep(self.delay)

    def reset(self):
        if self.ended:
            self.stop = False
            self.ended = False
            self.thread = Thread(target=self.run).start()



def manage_jack(robot):

    def start():
        print "[+] Actionning robot"
        robot.start()

    def abort():
        print "[-] Stopping robot because of jack"
        robot.stop()

    transitions = {'waiting':{'push':('ready', None)},
                    'ready':{'pull':('started', start)},
                    'started':{'push':('abort', abort)}}

    cur_state = 'waiting'

    def manage_jack_closure(pulled):
        if pulled:
            key = 'pull'
        else:
            key = 'push'

        if cur_state not in transitions:
            print "[-] Inexisting transition for state "+cur_state
            return

        if transitions[cur_state][key] is not None:
            cur_state, callback = transitions[cur_state][key]
            if callback is not None:
                callback()

    return manage_jack_closure




def add_jack_and_delay(robot, delay, start_waiting_jack = True):
    time_elapsed(5, lambda: manage_time_elapsed(robot))

    wait_object = Wait_Object()
    robot.add_method(lambda self: wait_object.stop(), 'start')

    robot.add_sequence('loop_before_start')
    robot.add_parallel((lambda u: wait_object.set_callback(callback=u), True))
    robot.wait()
    robot.sequence_done()

    robot.add_method(lambda self: robot.start_sequence('loop_before_start'), 'wait_for_jack_pulled')

    if start_waiting_jack:
        robot.wait_for_jack_pulled()

    return manage_jack(robot)
