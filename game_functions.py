from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import numpy as np
import collections
import random
from map_functions import *
from path_functions import *

  

def get_citytile_action(citytile, player ,added_units ,added_research ,cnn,units_info=None):
    
    thers = 0

    action = None
    
    ann=[]
        
    #print("cities :",len(player.cities.values()))
    #print("units :",len(player.units))
    
    step_cost = GAME_CONSTANTS["PARAMETERS"]["UNIT_ACTION_COOLDOWN"]["WORKER"]
    
    citytile_count = 0
    
    #nearest_resource_distance = game_state.distance_from_resource[city_tile.pos.y, city_tile.pos.x]
    
    
    resource_tiles  = find_tiles(cnn["resource_for_fuel"] , blocks = None , pos = citytile.pos)

    closest_resource_tile ,path ,path_dist,annt= find_closest_tile(citytile, player, resource_tiles,cnn ,
                                                                 benifit_map = [],
                                                                 blocks =[cnn['ob_blocks']  ,cnn['my_citytile_can_surv2end']],
                                                                 fast=True ,step_cost = step_cost )
    
    travel_range = units_info["turns_to_night"] // step_cost
    resource_in_travel_range = path_dist < travel_range


    
    for city in player.cities.values():
        for c in city.citytiles:
            citytile_count += 1
    
    if citytile_count > len(player.units) + added_units and resource_in_travel_range:

        if random.random() >thers:
            ann.append(annotate.text(citytile.pos.x, citytile.pos.y, "make worker", fontsize = 16))
            action =  citytile.build_worker()
        else:
            ann.append(annotate.text(citytile.pos.x, citytile.pos.y, "make cart", fontsize = 16))
            action = citytile.build_cart()
            
        added_units +=1


    elif player.research_points + added_research < GAME_CONSTANTS["PARAMETERS"]['RESEARCH_REQUIREMENTS']['URANIUM']:
        ann.append(annotate.text(citytile.pos.x, citytile.pos.y, "research", fontsize = 16))
        action = citytile.research()
        added_research += 1
    
    else:
        ann.append(annotate.text(citytile.pos.x, citytile.pos.y, "nothing", fontsize = 16))
    
    
    return action ,added_units ,added_research , ann



def get_worker_action( unit, player, cnn  , need_fuel  ,units_info=None ,game_state=None):
    
    action = None
    
    ann = []
    
    
    wood_fuel = GAME_CONSTANTS['PARAMETERS']['RESOURCE_TO_FUEL_RATE']['WOOD']
    coal_fuel = GAME_CONSTANTS['PARAMETERS']['RESOURCE_TO_FUEL_RATE']['COAL']
    uranium_fuel = GAME_CONSTANTS['PARAMETERS']['RESOURCE_TO_FUEL_RATE']['URANIUM']
    
    worker_upkeep = GAME_CONSTANTS['PARAMETERS']['LIGHT_UPKEEP']['WORKER']
    
    
    worker_upkeep_wood = 1 if worker_upkeep  / wood_fuel < 1 else math.ceil(worker_upkeep / wood_fuel)
    worker_upkeep_coal = 1 if worker_upkeep  / wood_fuel < 1 else math.ceil(worker_upkeep / wood_fuel)
    worker_upkeep_uranium = 1 if worker_upkeep  / wood_fuel < 1 else math.ceil(worker_upkeep / wood_fuel)
    
    
    step_cost =  GAME_CONSTANTS['PARAMETERS']['UNIT_ACTION_COOLDOWN']['WORKER']
    
    
    day_l = GAME_CONSTANTS['PARAMETERS']['DAY_LENGTH']
    night_l = GAME_CONSTANTS['PARAMETERS']['NIGHT_LENGTH']
    all_day = day_l + night_l
    max_days = GAME_CONSTANTS['PARAMETERS']['MAX_DAYS']
    
    remain_steps = max_days - game_state.turn
    cycles = remain_steps / all_day
    remain_part = night_l if ((cycles - math.floor(cycles)*all_day) > night_l) else (cycles - math.floor(cycles)*all_day)
    
    worker_can_surv = False
    
    if unit.cargo.wood > worker_upkeep_wood*remain_part:
        worker_can_surv = True
        
    elif unit.cargo.coal > worker_upkeep_coal*(remain_part - math.floor(unit.cargo.wood/worker_upkeep_wood)):
        worker_can_surv = True
        
    elif unit.cargo.uranium > worker_upkeep_coal*(remain_part - math.floor(unit.cargo.wood/worker_upkeep_wood) - math.floor(unit.cargo.coal/worker_upkeep_coal)):
        worker_can_surv = True
    
    if not units_info["is_day_time"]:
        step_cost *=2
    
    #fig , ax = plt.subplots(1,6,figsize=(20,3))
    
    workers_but_current = cnn['my_unit'].copy()
    
    #ax[0].imshow(workers_but_current)
    
    workers_but_current[unit.pos.x,unit.pos.y] = 0
    
    
    #ax[1].imshow(workers_but_current)
    
    workers_but_current *= 1- cnn['my_citytile']
    
    #ax[2].imshow(1- cnn['my_citytile'])
    
    #ax[3].imshow(workers_but_current)
    
    #workers_but_current += cnn['my_unit_cart']
    
    #ax[4].imshow(workers_but_current)
    
    ob_blocks = np.zeros(cnn['ob_unit_worker'].shape)
    ob_blocks += cnn['ob_unit_worker'] 
    ob_blocks +=  cnn['ob_unit_cart'] 
    ob_blocks +=  cnn['ob_citytile']
    
    
    benifit_map = cnn['can_mine'].copy()  #np.zeros(cnn['can_mine'].shape)
    #benifit_map += cnn['can_mine']
    
    
    #plt.show()
    
    #resource_tiles  = find_tiles(cnn['can_mine'] , pos = unit.pos)
    
    
    
    #can_sur = 1
    
    
    
    
    if need_fuel :
        #resource_tiles = 
        
        
        if unit.get_cargo_space_left() > 0:
            # find the closest resource if it exists to this unit my_citytile_can_surv2end
            resource_tiles  = find_tiles(cnn["resource_for_fuel"] , blocks = None , pos = unit.pos)
            
            #print(resource_tiles)
            
            closest_resource_tile ,path ,path_dist,annt= find_closest_tile(unit, player, resource_tiles,cnn ,
                                                                 benifit_map = [benifit_map],
                                                                 blocks =[workers_but_current ,cnn['ob_blocks']  ,cnn['my_citytile_can_surv2end']],
                                                                 fast=True ,step_cost = step_cost )
            
            ann.extend(annt)
            
            
            if closest_resource_tile is not None:
                #ann.append(annotate.circle(closest_resource_tile['pos'].x, closest_resource_tile['pos'].y))
                #ann.append(annotate.sidetext(f"{path}"))
                
           
                
                if(path is not None):
                    
                    if(len(path) > 1):
                        dire = unit.pos.direction_to(Position(*path[1]))
                        
                        if(units_info["is_day_time"] or worker_can_surv or
                           (cnn['my_citytile'][unit.pos.x,unit.pos.y] < 1 and
                            cnn['can_mine'][unit.pos.x,unit.pos.y] < 1) or
                          cnn['my_citytile'][path[1][0],path[1][1]] > 0  or
                           cnn['can_mine'][path[1][0],path[1][1]] > 0):
                            
                            action = unit.move(dire)


                        cnn['my_unit'][unit.pos.x,unit.pos.y] -= 1 
                        cnn['my_unit'][path[1][0],path[1][1]] += 1 
                    
                        
                
                

        else:
            # find the closest citytile and move the unit towards it to drop resources to a citytile to fuel the city
            citytiles_tiles = find_tiles(cnn['my_citytile']  , blocks = [cnn['my_citytile_can_surv2end']] , pos = unit.pos)
            closest_city_tile ,path ,path_dist,annt= find_closest_tile(unit, player, citytiles_tiles,cnn ,
                                                             benifit_map = [benifit_map],
                                                             blocks = [workers_but_current ,cnn['ob_blocks'] ,cnn['my_citytile_can_surv2end']],
                                                             fast=True ,step_cost = step_cost )
            
            ann.extend(annt)
            
            if closest_city_tile is not None:

                

                #ann.append(annotate.circle(closest_city_tile['pos'].x, closest_city_tile['pos'].y))
                #ann.append(annotate.sidetext(f"{path}"))
                
                #if(path is not None):
                if(len(path) > 1):
                    dire = unit.pos.direction_to(Position(*path[1]))
                        
                    if(units_info["is_day_time"] or worker_can_surv > 20 or
                           (cnn['my_citytile'][unit.pos.x,unit.pos.y] < 1 and
                            cnn['can_mine'][unit.pos.x,unit.pos.y] < 1) or
                          cnn['my_citytile'][path[1][0],path[1][1]] > 0  or
                           cnn['can_mine'][path[1][0],path[1][1]] > 0):
                            
                        action = unit.move(dire)

                    cnn['my_unit'][unit.pos.x,unit.pos.y] -= 1 
                    cnn['my_unit'][path[1][0],path[1][1]] += 1
                
                
    else:
        
        if unit.get_cargo_space_left() > 0:
            # find the closest resource if it exists to this unit
            
            resource_tiles  = find_tiles(cnn['resource_for_build'] ,blocks=[cnn['my_citytile']], pos = unit.pos)
            closest_resource_tile ,path ,path_dist, annt = find_closest_tile(unit, player, resource_tiles ,
                                                                  cnn,benifit_map = [benifit_map,cnn['can_build']],
                                                           blocks =[workers_but_current ,cnn['ob_blocks']],
                                                                  fast=True ,step_cost = step_cost )
            
            ann.extend(annt)
            #print(path)
            if closest_resource_tile is not None:
                #ann.append(annotate.circle(closest_resource_tile['pos'].x, closest_resource_tile['pos'].y))
                
                #if(path is not None):
                if(len(path) > 1):
                    dire = unit.pos.direction_to(Position(*path[1]))
                        
                    if(units_info["is_day_time"] or worker_can_surv or
                           (cnn['my_citytile'][unit.pos.x,unit.pos.y] < 1 and
                            cnn['can_mine'][unit.pos.x,unit.pos.y] < 1) or
                          cnn['my_citytile'][path[1][0],path[1][1]] > 0  or
                           cnn['can_mine'][path[1][0],path[1][1]] > 0):
                            
                            
                        action = unit.move(dire)

                    cnn['my_unit'][unit.pos.x,unit.pos.y] -= 1 
                    cnn['my_unit'][path[1][0],path[1][1]] += 1
                
        else:
            build_tiles = find_tiles(cnn['can_build'] , pos = unit.pos)
            closest_build_tile ,path ,path_dist,annt = find_closest_tile(unit, player, build_tiles,
                                                              cnn ,benifit_map = [benifit_map],
                                                        blocks =  [workers_but_current ,cnn['ob_blocks'] ,cnn['my_citytile']],
                                                              fast=True ,step_cost = step_cost )
            
            ann.extend(annt)
            if closest_build_tile is not None:
                
                #ann.append(annotate.x(closest_build_tile['pos'].x, closest_build_tile['pos'].y))
                if closest_build_tile['pos'].equals(unit.pos):
                    action = unit.build_city()
                
                else:

                    #if(path is not None):
                    if(len(path) > 1):
                        dire = unit.pos.direction_to(Position(*path[1]))
                            
                        if(units_info["is_day_time"] or worker_can_surv or
                           (cnn['my_citytile'][unit.pos.x,unit.pos.y] < 1 and
                            cnn['can_mine'][unit.pos.x,unit.pos.y] < 1) or
                          cnn['my_citytile'][path[1][0],path[1][1]] > 0  or
                               cnn['can_mine'][path[1][0],path[1][1]] > 0):
                                
                                
                            action = unit.move(dire)

                        cnn['my_unit'][unit.pos.x,unit.pos.y] -= 1 
                        cnn['my_unit'][path[1][0],path[1][1]] += 1
            
            
            
        
            
    return action ,ann


def get_cart_action( unit, player, cnn  , need_fuel  ,units_info=None ,game_state=None):
    
    action = None
    
    ann = []
    
       
    return action ,ann
