from enum import Enum

class ClusterType(Enum):
    CITY = 1
    RESOURCE = 2

    
    
def init():

    #def init():
    global cashed_roads
    cashed_roads = {}

    global current_turn
    current_turn = 0

    #global global_ss
    #global_ss = "i am global"