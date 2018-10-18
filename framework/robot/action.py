from threading import Thread, Condition, Lock
from AX12 import AX12
import time
debug = True

class Action:
    '''
    Represents any action or group of actions a robot can make.
    The actions can be defined as a tree with sequences as nodes and function
    calls as leaves.
    '''
    def __init__(self, callback : callable = lambda : None):
        # callback is called when an action is over
        self.callback = callback
        self.to_be_waited = False
        self.timeout = None
        self.parent_sequence = None
        self.done = False
        # Conditional variable : an object that allows a thread to wait for an event 
        # from another thread. Used to wait for actions to end.
        self.done_condvar = Condition()

    def private_callback(self):
        '''
        This function is called when the action is finished.
        '''
        self.done_condvar.acquire()
        self.done = True
        self.done_condvar.notify()
        if not self.callback is None:
            self.callback()
        if not self.parent_sequence is None:
            self.parent_sequence.element_callback()
        self.done_condvar.release()

    def wait(self, timeout : float = None) -> 'Action':
        '''
        Sets the to_be_waited flag: action callbacks will be waited for before
        continuing execution
        '''
        if(self.callback is None):
            raise(Error("Cannot wait an action without callback"))
        else:
            self.to_be_waited = True
            self.timeout = timeout
        return self
    
    def exec(self):
        self.private_exec()
        if(self.to_be_waited):
            self.done_condvar.acquire()
            t0 = time.time()
            t1 = t0
            while not self.done:
                self.done_condvar.wait(self.timeout - (t1 - t0))
                t1 = time.time()
                if ((t1 - t0) >= self.timeout) and not self.done:
                    print(self, "timed out.")
                    self.cancel_exec()
                    break
            self.done_condvar.release()

    def cancel_exec(self):
        if(not (self.callback is None or self.parent_sequence is None)):
            self.parent_sequence.element_cancel()

class Sequence(Action):
    '''
    A sequence is a collection of actions
    '''
    def __init__(self, name = None, callback : callable = lambda : None):
        Action.__init__(self, callback)
        self.action_list = []
        self.current_action_idx = 0
        self.nb_callbacks = 0
        self.name = name
        # A lock preventing a simultaneous construction and execution of the sequence
        self.mutex = Lock()

    def __str__(self) -> str:
        if not self.name is None:
            return "Sequence " + self.name
        else:
            return "Unnamed sequence"

    def add_action(self, action : Action, position : int = -1) -> 'Sequence':
        '''
        Adds an action in the sequence at the given position.
        '''
        self.mutex.acquire()
        position = len(self.action_list) if position == -1 else position
        position = max(self.current_action_idx, position)
        self.action_list.insert(position, action)
        if(not action.callback is None):
            self.nb_callbacks += 1
        action.parent_sequence = self
        self.mutex.release()
        return self

    def add_actions(self, actions) -> 'Sequence':
        '''
        Takes a list of actions and adds it in order to the sequence.
        '''
        for action in actions:
            self.add_action(action)
        return self

    def element_callback(self):
        '''
        Called whenever an action of the sequence executes its callback.
        Allows to count the number of callbacks left.
        '''
        self.mutex.acquire()
        self.nb_callbacks -= 1
        print("Callback received in sequence", self.name, ",", \
                self.nb_callbacks, "expected callbacks left")
        # If all expected callbacks have been received, call the sequence callback
        if(self.nb_callbacks == 0):
            self.mutex.release()
            self.private_callback()
        else:
            self.mutex.release()

    def element_cancel(self):
        '''
        Called when an element of the sequence cancels its execution, in particular
        in a timeout situation.
        '''
        self.mutex.acquire()
        self.nb_callbacks -= 1
        print("Element execution canceled in sequence", self.name, ",", \
                self.nb_callbacks, "expected callbacks left")
        # If all expected callbacks have been received, call the sequence callback
        if(self.nb_callbacks == 0):
            self.mutex.release()
            self.private_callback()
        else:
            self.mutex.release()

    def private_exec(self):
        '''
        Is called by the Action.exec() function. Executes the actions of all elements of
        the sequence.
        '''
        while self.current_action_idx < len(self.action_list):
            if debug:
                print("Executing action number", self.current_action_idx, \
                       "in sequence", self.name)
            self.mutex.acquire()
            action = self.action_list[self.current_action_idx]
            self.current_action_idx += 1
            self.mutex.release()
            action.exec()
            
    def add_path(self, robot, path, max_delay=15):
        """
        Defines a list of MoveToAction to follow a list of points [(x0, y0), (x1, y1), ...]
        These actions are added to the sequence.
        Don't forget that the orientation at the end of the path is not specified!
        """
        for x, y in path:
            self.add_action(MoveToAction(robot, x, y))

class Function(Action):
    '''
    A function call, with the options of callback
    '''
    def __init__(self, \
                 function, \
                 args = [], \
                 callback : callable = lambda : None):
        Action.__init__(self, callback)
        if(not self.callback is None):
            self.function = lambda cb: function(*(args + [cb]))
        else:
            self.function = lambda: function(*args)

    def __str__(self):
        return "Funtion call"

    def private_exec(self):
        if(not self.callback is None):
            self.function(self.private_callback)
        else:
            self.function()

class ThreadedFunction(Function):
    '''
    A function call in a new thread
    '''
    def __init__(self, \
                 function, \
                 args = [], \
                 callback : callable = lambda : None):
        self.thread = Thread(target = function, args = args)
        Function.__init__(self, lambda : self.thread.start(), [], callback)

class MoveToAction(Function):
    '''
    Action moving to position and angle
    '''
    def __init__(self, \
                 robot, \
                 x : int, \
                 y : int, \
                 angle : int = -1):
        Function.__init__(self, robot.moveTo, [x, y, angle])

class AX12MoveAction(Function):
    '''
    Move action of an AX12
    '''
    def __init__(self, \
                 ax12 : AX12, \
                 position : int,
                 cancel_position : int = None):
        Function.__init__(self, ax12.move, [position])
        self.ax12 = ax12
        self.cancel_position = cancel_position

