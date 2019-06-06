from threading import Thread
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
        # parent_callback is used to count the number of callbacks in a
        # sequence
        self.to_be_waited = False
        self.parent_sequence = None

    def private_callback(self):
        '''
        This function is called when the action is finished.
        '''
        if(not self.callback is None):
            self.callback()
        if(not self.parent_sequence is None):
            self.parent_sequence.element_callback(self)
        else if(self.to_be_waited):
            waiting_for_callback = False

    def wait(self) -> 'Action':
        '''
        Sets the to_be_waited flag: action callbacks will be waited for before
        continuing execution
        '''
        if(self.callback is None):
            raise(Error("Cannot wait an action without callback"))
        else:
            self.to_be_waited = True
        return self

    def exec(self):
        '''
        Has to be called in the end of all overriden exec in order to prevent the
        program from being killed if the callback has to be waited for.
        '''
        if(self.to_be_waited && self.parent_sequence == None):
            self.waiting_for_callback = True
            while(waiting_for_callback):
                pass


class Sequence(Action):
    '''
    A sequence is a collection of actions
    '''
    def __init__(self, callback : callable = lambda : None, name : str = None):
        Action.__init__(self, callback)
        self.action_list = []
        self.current_action_idx = 0
        self.nb_callbacks = 0
        self.name = name

    def add_action(self, action : Action) -> 'Sequence':
        self.action_list.append(action)
        if(not action.callback is None):
            self.nb_callbacks += 1
        # New callback to count the number of callbacks
        action.parent_sequence = self
        return self

    def add_actions(self, actions) -> 'Sequence':
        for action in actions:
            self.add_action(action)
        return self

    # parent_callback for actions in the sequence
    def element_callback(self, action):
        print("Callback received in sequence", self.name)
        self.nb_callbacks -= 1
        # If the action was being waited for, the execution has to be resumed
        if(action.to_be_waited):
            self.exec()
        # If all expected callbacks have been received, call the sequence callback
        if(self.nb_callbacks == 0):
            self.private_callback()

    def exec(self):
        while self.current_action_idx < len(self.action_list):
            if debug:
                print("Executing action number", self.current_action_idx, \
                       "in sequence", self.name)
            action = self.action_list[self.current_action_idx]
            action.exec()
            self.current_action_idx += 1
            if(action.to_be_waited):
                break

    def add_path(self, path, max_delay=15):
        """
        defines a list of moveTo to follow a list of points [(x0, y0), (x1, y1), ...]
        These actions are added to the sequence which is currently being defined
        It's not yet executed!
        Don't forget that the orientation at the end of the path is not specified!
        """
        for x, y in path:
            self.add_parallel(self.moveTo, [x, y, -1])
            self.wait(max_delay=max_delay)

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

    def exec(self):
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
