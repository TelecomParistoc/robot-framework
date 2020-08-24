from robot import Robot
from action import Action
from typing import Iterable

class Mission:
    def __init__(self, root_action : Action, position, estimated_points : int, estimated_time : int, timeout : int, min_date : int, max_date):
        self.root_action = root_action
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

    def __init__(self, mission_list : Iterable, robot : Robot):
        self.mission_list = mission_list

    def eval(self, mission) -> int:
        '''
        This function returns an evaluation of the quality of a mission
        at the current time.
        You need to override it.
        '''
        return 0

    def best_mission(self) -> Mission:
        '''
        This function returns the mission with the highest evaluation.
        '''

        mission_eval = [ (mission, eval(mission)) for mission in self.mission_list]
        if(len(mission_eval) == 0): return None

        sorted_missions = sorted(mission_eval, key=lambda mission: mission[2], reverse=True)

        return sorted_missions[0][0]
