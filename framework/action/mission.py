from robot import Robot
from action import Action

class Mission:
    def __init__(self, \
                 root_action : Action, \
                 position, 
                 estimated_points : int, \
                 estimated_time : int\
                 timeout  : int\
                 min_date : int
                 max_date : int):
        self.root_action = action
        self.position = position
        self.estimated_points = estimated_points
        self.estimated_time = estimated_time
        self.timeout = timeout
        self.min_date = min_date
        self.max_date = max_date

class MissionStrategy:
    '''
    This class is used to make a mission choice.
    It has to be overriden in order to define the eval function.
    '''
    def __init__(self, mission_list, robot : Robot):
        self.mission_list = mission_list

    def eval(self, mission) -> int:
        '''
        This function returns an evaluation of the quality of a mission
        at the current time.
        You need to override it.
        '''
        return 0

    def best_mission() -> mission:
        '''
        This function returns the mission with the highest evaluation.
        '''
        if(len(mission_eval) == 0) return None

        mission_eval = [mission, eval(mission) for mission in self.mission_list]
        choice = mission_eval[0]
        for(x in mission_eval[1:]):
            if(x[1] > choice[1]):
                choice = x
        return x[0]
