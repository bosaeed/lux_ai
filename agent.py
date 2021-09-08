from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import numpy as np
from game_functions import *
from map_functions import *
from path_functions import *
import time
import settings  


    
game_state = None
def agent(observation, configuration=None , debug = False ,cash = {}):
    global game_state
    
    #global global_ss
    #print(global_ss)
    #global_ss = "changed"
    #print(global_ss)
    
    day_l = GAME_CONSTANTS['PARAMETERS']['DAY_LENGTH']
    night_l = GAME_CONSTANTS['PARAMETERS']['NIGHT_LENGTH']
    

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
        
        settings.init()
        
        
        
    else:
        game_state._update(observation["updates"])
    
    actions = []
    
    
    agent_start_time = time.time()
    
    

    ### AI Code goes down here! ### 
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height
    
    cnn ,units_info = get_cnn_data(game_state,player ,opponent , width , height)
    
    agent_cnn_time = time.time()-agent_start_time
    
    # add debug statements like so!
    if game_state.turn == 0:
        print("Agent is running!")
      
    settings.current_turn = game_state.turn
    
    #if settings.current_turn % 50 == 0:
    #    cashed_roads.clear()
    '''    
    units_info["night_turns_left"] = night_turns_left
    units_info["turns_to_night"] = turns_to_night

    units_info["turns_to_dawn"] = turns_to_dawn

    units_info["is_day_time"] = is_day_time
    '''
    
    
    
    need_fuel = True
    
    if len(player.cities) == 0:
        need_fuel = False
        

                    
    added_units=0
    added_research=0
    
    
    for city in player.cities.values():
        
        if city.fuel > city.get_light_upkeep() * night_l and units_info["is_day_time"] and units_info["turns_to_night"] > 10:
            need_fuel = False
            
            
        for citytile in city.citytiles:       
            if citytile.can_act():
                
                action ,added_units , added_research ,ann= get_citytile_action(citytile,player,
                                                                               added_units ,added_research ,cnn,units_info=units_info)
                
                
                if action is not None:
                    actions.append(action)
                  
                #for an in unit_ann:
                actions.extend(ann)
                
                    
    units_time = []
    for unit in player.units:
        # if the unit is a worker (can mine resources) and can perform an action this turn
        unit_ann = []
        
        start_time = time.time()
        if unit.can_act():
            if unit.is_worker():

                action ,unit_ann = get_worker_action(unit, player ,cnn, need_fuel ,units_info=units_info ,game_state=game_state)

                if action is not None:
                    actions.append(action)

                #for an in unit_ann:
                actions.extend(unit_ann)
                        
            else:
                
                action ,unit_ann = get_cart_action(unit, player ,cnn, need_fuel ,units_info=units_info ,game_state=game_state)

                if action is not None:
                    actions.append(action)

                #for an in unit_ann:
                actions.extend(unit_ann)
            
            
            units_time.append(time.time() - start_time) 
                    
        
    
    
    if debug:
        unit_t = 0
        if len(units_time)>0:
            unit_t = sum(units_time)/len(units_time)
            #print('agent step time :',time.time() - agent_start_time)
            #print('agent cnn time :',agent_cnn_time)
        return actions , cnn ,unit_t
    return actions