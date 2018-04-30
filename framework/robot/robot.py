from threading import Thread, Lock
import types
import time

import motion

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

        self.expected_callback_indexes = []
        self.current_callback_index = 0

        if moving_interface:
            for motion_attribute in dir(motion):
                if callable(motion_attribute):
                    self.add_method(getattr(motion, motion_attribute))

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
        return True

    def add_parallel_thread(self, function, arg_list, count_enable=True, force_root_seq=False):
        """
            same as add_parallel but function is launched in a separated Thread
        """
        self.add_parallel(
            lambda: Thread(target=function, args=arg_list).start(), [],
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


    def run(self):
	spam_console = True
        self.started = True
        self.paused = False
        prev_time = time.time()
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
                    deltime = time.time()-prev_time
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
                            prev_time = time.time()

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
                                prev_time = time.time()
                                self.reset_waited_callbacks_release_acquire_launch_sequence()

                                if self.debug:
                                    print("[+++] Parallel block "+str(prev_parallel)+" done, all actions of sequence "+prev+" has been done, we return to "+seq+" sequence")
                            else:
                                prev_time = time.time()
                                self.reset_waited_callbacks_release_acquire_launch_sequence(self.cur_parallel)
                                if self.debug:
                                    if self.cur_sequence != "":
                                        print("[+] Parallel block "+str(self.cur_parallel)+" done in sequence "+self.cur_sequence+"; continuing")

                self.sequence_mutex.release()

            time.sleep(0.01)
        print("[+++] Sequence thread ended")


    def stop(self):
        self.started = False
        if self.debug:
            print("[++][...] Stopping sequence thread")

    def is_running(self):
        return self.started
