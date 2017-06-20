from threading import Thread, Lock
import types
import time


class Robot:

    def __init__(self, debug=True):
        self.debug = debug
        self.received_callbacks = 0

        self.cur_sequence = ""
        self.cur_parallel = 0
        self.cur_sequence_constructed = ""
        self.temp_delays = []
        self.temp_sequence = [[]]
        self.temp_expected_callbacks = [0]
        self.delays = {'':[]}
        self.sequences = {'':[[]]}
        self.expected_callbacks = {'':[]}
        self.sequence_queue = []
        self.sequence_mutex = Lock()

        self.started = False
        self.thread = Thread(target=lambda: self.run()).start()



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
            return
        elif self.cur_sequence_constructed != "":
            print("[-] There must not be a current sequence filled, no sequence added")
            return

        self.sequences[name] = []
        self.temp_delays = []
        self.temp_sequence = [[]]
        self.temp_expected_callbacks = [0]
        self.cur_sequence_constructed = name

        if self.debug:
            print("[+] New sequence added with name "+self.cur_sequence_constructed+"; now fill it")

        self.sequence_mutex.release()



    def sequence_done(self):
        self.sequence_mutex.acquire()

        if self.cur_sequence_constructed == "":
            print("[-] Root sequence could never be done")
            return

        if len(self.temp_delays) < len(self.temp_sequence):
            self.temp_delays.append(-1.0)
            if len(self.temp_delays) != len(self.temp_sequence):
                print("[-] Strange thing detected, should not happen (delays table must have the same length as sequence table). Contact admin")
                return

        self.delays[self.cur_sequence_constructed] = self.temp_delays
        self.sequences[self.cur_sequence_constructed] = self.temp_sequence
        self.expected_callbacks[self.cur_sequence_constructed] = self.temp_expected_callbacks
        if self.debug:
            print("[+] New sequence "+self.cur_sequence_constructed+" has been completed, it is made of "+str(len(self.temp_sequence)))

        self.cur_sequence_constructed = ""
        self.temp_delays = []
        self.temp_sequence = [[]]
        self.temp_expected_callbacks = [0]

        self.sequence_mutex.release()



    def add_parallel(self, to_call_and_is_callback):
        self.sequence_mutex.acquire()

        number_parallels = len(self.temp_sequence)-1
        self.temp_sequence[-1].append(to_call_and_is_callback[0])

        if to_call_and_is_callback[1]:
            self.temp_expected_callbacks[-1] += 1
            if self.debug:
                if self.cur_sequence_constructed == "":
                    print("[.] Function with callback added to root sequence at step "+str(number_parallels))
                else:
                    print("[.] Function with callback added to current sequence "+self.cur_sequence_constructed+" at step "+str(number_parallels))
        elif self.debug:
            if self.cur_sequence_constructed == "":
                print("[.] Function with no callback added to root sequence at step "+str(number_parallels))
            else:
                print("[.] Function with no callback added to current sequence "+self.cur_sequence_constructed+" at step "+str(number_parallels))

        self.sequence_mutex.release()



    def wait(self, max_delay=-1.0, n_callbacks=0):
        self.sequence_mutex.acquire()

        if self.cur_sequence_constructed == "":
            self.temp_delays = [max_delay]
            if self.temp_expected_callbacks[-1] < n_callbacks:
                self.temp_expected_callbacks[-1] = n_callbacks

            self.delays[self.cur_sequence_constructed].extend(self.temp_delays)
            self.sequences[self.cur_sequence_constructed].extend(self.temp_sequence[-1])
            self.expected_callbacks[self.cur_sequence_constructed].extend(self.temp_expected_callbacks)

            self.temp_delays = [0]
            self.temp_sequence = [[]]
            self.temp_expected_callbacks = [0]
        else:
            self.temp_delays.append(max_delay)
            self.temp_sequence.append([])
            self.temp_expected_callbacks.append(n_callbacks)

        if self.debug:
            if self.cur_sequence_constructed == "":
                print("[.] New step added to root sequence after a delay of "+str(max_delay))
            else:
                print("[.] New step added to current sequence "+self.cur_sequence_constructed+" after a delay of "+str(max_delay))

        self.sequence_mutex.release()



    def launch_sequence(self, step):
        self.sequence_mutex.acquire()
        for s in self.sequences[self.cur_sequence][step]:
            self.sequence_mutex.release()
            s()
            self.sequence_mutex.acquire()
        self.sequence_mutex.release()


    def start_sequence(self, name):
        self.sequence_mutex.acquire()

        if self.cur_sequence == "":
            self.cur_sequence = name
            self.last_sequence = name
            self.cur_parallel = 0
            self.sequence_mutex.release()
            self.launch_sequence(self.cur_parallel)
            self.sequence_mutex.acquire()
            if self.debug:
                print("[+] Starting sequence "+self.cur_sequence+" over root sequence")
        else:
            if self.debug:
                print("[.] Continuing sequence "+self.cur_sequence+" and adding "+name+" to queue")
            self.sequence_queue.append(name)

        self.sequence_mutex.release()

        if not self.started:
            self.thread = Thread(target=lambda: self.run()).start()



    def start_last_used(self, step=0):
        self.sequence_mutex.acquire()

        if self.cur_sequence == "":
            if self.debug:
                print("[+] Starting sequence "+self.last_sequence+" over root sequence at step "+str(step))
        else:
            if self.debug:
                print("[+] Starting sequence "+self.last_sequence+" over "+self.cur_sequence+" at step "+str(step))

        self.cur_sequence = self.last_sequence
        self.cur_parallel = step
        self.sequence_mutex.release()

        if not self.started:
            self.thread = Thread(target=lambda: self.run()).start()



    def wait_sequence(self, until_the_end=False, wait_until_the_end_of_root_sequence=False):
        self.sequence_mutex.acquire()

        if self.cur_sequence == "" and not wait_until_the_end_of_root_sequence:
            print("[-] Waiting for root sequence to finish is useless when wait_until_the_end_of_root_sequence==False, nothing done")
            return

        base = self.cur_sequence

        if self.debug:
            if base == "":
                print("[...] Waiting for root sequence to finish")
            else:
                print("[...] Waiting for sequence "+base+" to finish")
        while ((self.cur_sequence == base and base != "") and not until_the_end) or (self.cur_sequence != '' and until_the_end):
            self.sequence_mutex.release()
            time.sleep(0.01)
            self.sequence_mutex.acquire()

        if self.cur_sequence == "" and wait_until_the_end_of_root_sequence:
            while self.cur_parallel>=0:
                self.sequence_mutex.release()
                time.sleep(0.01)
                self.sequence_mutex.acquire()

        if self.debug:
            if base == "":
                if self.cur_sequence == '':
                    print("[+] Root Sequence is finished, cleaning root")
            else:
                if self.cur_sequence == '':
                    print("[+] Sequence "+base+" is finished, returning to root sequence")
                else:
                    print("[+] Sequence "+base+" is finished, returning to "+self.cur_sequence+" sequence")

        self.sequence_mutex.release()



    def receive_callback(self):
        self.sequence_mutex.acquire()
        self.received_callbacks += 1
        if self.debug and self.expected_callbacks.get(self.cur_sequence) is not None and self.cur_parallel<self.expected_callbacks[self.cur_sequence]:
            print("[+] One more callback received (count : "+str(self.received_callbacks)+") out of "+str(self.expected_callbacks[self.cur_sequence][self.cur_parallel]))
        elif self.debug:
            print("[-] One more callback received (count : "+str(self.received_callbacks)+") but no expected callback")
        self.sequence_mutex.release()



    def pause(self):
        self.paused = True
        if self.debug:
            print("[...] Pausing thread")


    def unpause(self):
        self.paused = False
        if self.debug:
            print("[+] Unpausing thread")


    def run(self):
        self.started = True
        self.paused = False
        prev_time = time.time()
        print("[+] Starting sequence thread")
        while self.started:
            if not self.paused:
                self.sequence_mutex.acquire()

                if self.cur_sequence == "" and len(self.sequences[self.cur_sequence][0]) == 0 and len(self.delays[self.cur_sequence]) == 0:
                    print("[...] No action in root sequence, doing nothing")
                else:
                    deltime = time.time()-prev_time
                    #print self.cur_sequence, self.cur_parallel, len(self.delays), len(self.delays[self.cur_sequence]), self.received_callbacks, self.expected_callbacks[self.cur_sequence]
                    if (self.delays[self.cur_sequence][self.cur_parallel]>0 and deltime>self.delays[self.cur_sequence][self.cur_parallel]) or self.received_callbacks >= self.expected_callbacks[self.cur_sequence][self.cur_parallel]:
                        print(self.expected_callbacks[self.cur_sequence][self.cur_parallel])
                        self.received_callbacks = 0
                        self.cur_parallel += 1
                        if self.cur_parallel >= len(self.sequences[self.cur_sequence]):
                            if self.cur_sequence == '':
                                if self.debug:
                                    print("[++] All actions of root sequence has been done, no more actions")
                                self.sequences[self.cur_sequence] = [[]]
                                self.delays[self.cur_sequence] = [0]
                                self.expected_callbacks[self.cur_sequence] = [0]
                                self.cur_parallel = -1
                            else:
                                if len(self.sequence_queue)>0:
                                    seq = self.sequence_queue[0]
                                    self.cur_sequence = seq
                                    del self.sequence_queue[0]
                                else:
                                    seq = 'root'
                                    self.cur_sequence = ''

                                self.cur_parallel = 0
                                self.sequence_mutex.release()
                                self.launch_sequence(0)
                                self.sequence_mutex.acquire()

                                if self.debug:
                                    print("[++] All actions of sequence "+self.cur_sequence+" has been done, we return to "+seq+" sequence")
                            self.cur_parallel
                        else:
                            self.sequence_mutex.release()
                            self.launch_sequence(self.cur_parallel)
                            self.sequence_mutex.acquire()
                            if self.debug:
                                print("[+] Parallel block "+str(self.cur_parallel)+" done in sequence "+self.cur_sequence+"; continuing")

                self.sequence_mutex.release()

            time.sleep(0.01)
        print("[+] Ending sequence thread")


    def stop(self):
        self.started = False
        if self.debug:
            print("[+] Stopping sequence thread")



if __name__ == "__main__":

    class AX12:

        def __init__(self, id):
            self.id = id

        def move_to(self, position=(0,0), callback=None):
            print("[!!] We are moving in AX12 "+str(self.id)+" to "+str(position)+" (to be replaced with interface code)")
            self.callback = callback
            t = Thread(target=lambda: self.run()).start()

        def run(self):
            time.sleep(2.5)
            if self.callback is not None:
                self.callback()

    class Singleton(type):

        _instances = {}

        def __call__(cls, *args, **kwargs):
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[cls]


    class Moving_Interface:
        __metaclass__ = Singleton

        def move_to(self, robot, position):
            print("[!!] We are moving to "+str(position)+" (to be replaced with interface code)")


    moving_interface = Moving_Interface()




    robot_skeleton = Robot()

    def open_AX12_pinces(r):
        r.AX12_pinces1.move_to((15, 300))
        r.AX12_pinces2.move_to((85, 70))


    def useless_function(robot):
        print "Insert your useless sentence here"


    def init():
        robot_skeleton.add_object(AX12(125), 'AX12_pinces1')
        robot_skeleton.add_object(AX12(132), 'AX12_pinces2')
        robot_skeleton.add_methods_of_object(moving_interface)
        robot_skeleton.add_method(open_AX12_pinces, 'open_AX12_pinces')
        robot_skeleton.add_method(useless_function, 'useless')

        return robot_skeleton



    #to replace by move of moving_interface
    def move(robot, x, y, t):
        print "Moving from "+str(x)+" to "+str(y)+" during "+str(t)
        time.sleep(t)
        robot.receive_callback()

    def ax12_up():
        print "Moving ax12 test"

    robot = init()
    robot.AX12_pinces1.move_to((100, 20))                         #no callback => impossible to wait the end of the action
    robot.AX12_pinces2.move_to((200, 10), robot.receive_callback) #callback specified => now robot is able to wait for the end of a number of actions we specify
    robot.wait(10, 1)                                             #robot waits for 1 callback during a maximum delay of 10s
    #robot.wait_sequence(until_the_end=True, wait_until_the_end_of_root_sequence=True)

    robot.add_sequence('first_seq')                                     #A sequence associated with a key is a set of actions that are not executed immediately but stored
    robot.add_parallel((lambda: move(robot, x=10, y=200, t=5), True))  #we specify the fact first function will call the receive_callback from robot object with the second member "True" of the pair
    robot.add_parallel((ax12_up, False))                                #simple action with no callback
    robot.wait()                                                        #by default robot waits receiving all callbacks during an infinite amount of time
    robot.add_parallel((lambda: robot.AX12_pinces1.move_to((250, 20), robot.receive_callback), True))
    robot.add_parallel((lambda: move(robot, x=30, y=250, t=1), True))
    robot.add_parallel((lambda: robot.useless(), False))                #function that is declared in big_robot.py and added to robot during init in big_robot.py
    robot.wait(max_delay=20)
    robot.add_parallel((lambda: robot.move_to((60, 500)), False))       #function that is declared in moving_interface.py and added to robot during init in big_robot.py
    robot.add_parallel((lambda: robot.open_AX12_pinces(), False))       #function that is declared in big_robot.py and added to robot during init in big_robot.py
    robot.sequence_done()                                               #this indicates the end of current sequence and reset


    #We can also execute sequence directly when we are not in a key associated sequence
    robot.add_parallel((ax12_up, False))
    robot.add_parallel((lambda: move(robot, x=-30, y=250, t=4), True))
    robot.wait(10)

    robot.start_sequence('first_seq')                           #launching sequence
    robot.wait_sequence()
    robot.start_last_used(step=1)                               #restarts the last used sequence at step 2 (numbering starts with 1)
    time.sleep(1)
    robot.pause()                                               #pausing a sequence is the only way not to get out of current sequence
    robot.unpause()                                             #sequence continues where it was paused

    robot.wait_sequence()
    robot.stop()
