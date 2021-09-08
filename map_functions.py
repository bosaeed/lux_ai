from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import numpy as np
import random
from game_functions import *
from path_functions import *
import collections
from settings import ClusterType




# ## Define helper functions


def update_4_way(array , x,y,w,h,amount=1 , corner = False , center = False):
    
    
    if center:
        array[x,y] += amount 
        
    for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                array[x2,y2] += amount
                
    if corner: 
        for x2, y2 in ((x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                array[x2,y2] += amount


def set_4_way(array , x,y,w,h,amount=1 , corner = False , center = False):
    
    
    if center:
        array[x,y] = amount 
        
    for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                array[x2,y2] = amount
                
    if corner: 
        for x2, y2 in ((x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                array[x2,y2] = amount


def get_4_way(array , x,y,w,h,amount=1 , corner = False , center = False , get_first = False):
    output = 0
    if center:
        output += array[x,y]*amount
        if get_first:
            return array[x,y]
        
    for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                output += array[x2,y2]*amount
                if get_first:
                    return array[x2,y2]
                
    if corner: 
        for x2, y2 in ((x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                output += array[x2,y2]*amount
                if get_first:
                    return array[x2,y2]
    
    
    return output



def check_4_way(array , x,y,w,h,amount=None , corner = False , center = False ):

    if center:
        if amount is None:
            if array[x,y] > 0:
                return array[x,y]
        else:
            if array[x,y] == amount:
                return array[x,y]
        
        
        
    for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                value = array[x2,y2]
                if amount is None:
                    if value > 0:
                        return value
                else:
                    if value == amount:
                        return value
                
    if corner: 
        for x2, y2 in ((x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)):
            if 0 <= x2 < h and 0 <= y2 < w :
                value = array[x2,y2]
                if amount is None:
                    if value > 0:
                        return value
                else:
                    if value == amount:
                        return value
    
    
    return 0

    


def get_cnn_data(game_state,player ,opp , w , h):
    
    layers = ["resource_location","is_uranium","is_wood"
              ,"is_coal","uranium_amount","wood_amount","coal_amount"
              ,"road_cooldown","my_citytile" ,"ob_citytile"
              #,"my_citytile_cool" ,"ob_citytile_cool"
              ,"my_unit","my_citytile_can_surv"
              ,"my_citytile_can_surv2end"
             ,"my_unit_worker" ,"ob_unit_worker"
              ,"my_unit_cart" ,"ob_unit_cart"
             ,"my_unit_worker_can_act" ,"ob_unit_worker_can_act"
             ,"my_unit_worker_cooldown" ,"ob_unit_worker_cooldown"
             ,"my_unit_worker_left_space" ,"ob_unit_worker_left_space"
             #,"my_unit_worker_uranium" ,"ob_unit_worker_uranium"
             #,"my_unit_worker_coal" ,"ob_unit_worker_coal"
             #,"my_unit_worker_wood" ,"ob_unit_worker_wood"
              ,"can_mine" , "is_empty" , "can_build"
             ,"my_city_need_build" , "resource_for_build"
             ,"resource_for_fuel" ,'ob_blocks'
             ,'resource_clusters','city_clusters'
             ,"roads"]
    
    #cnn = []
    layers_dic = {}
    
    clusters = {}
    
    
    day_l = GAME_CONSTANTS['PARAMETERS']['DAY_LENGTH']
    night_l = GAME_CONSTANTS['PARAMETERS']['NIGHT_LENGTH']
    all_day = day_l + night_l
    max_days = GAME_CONSTANTS['PARAMETERS']['MAX_DAYS']
    
    remain_steps = max_days - game_state.turn
    #print("remain_steps :",remain_steps)

    
    night_turns_left = (max_days - game_state.turn)//all_day * night_l + min(night_l, (max_days - game_state.turn)%all_day)

    turns_to_night = (day_l - game_state.turn)%all_day
    turns_to_night = 0 if turns_to_night > day_l else turns_to_night

    turns_to_dawn = (all_day - game_state.turn%all_day)
    turns_to_dawn = 0 if turns_to_dawn > night_l else turns_to_dawn

    is_day_time = turns_to_dawn == 0
    
    
    
    citytile_upkeep = GAME_CONSTANTS['PARAMETERS']['LIGHT_UPKEEP']['CITY']
    city_adj_bonus = GAME_CONSTANTS['PARAMETERS']['CITY_ADJACENCY_BONUS']
    
    #layers_dic = {name : np.zeros((max_w,max_h)) for name in layers}
    for name in layers:
        layers_dic[name] = np.zeros((w,h))
        
    layers_dic["is_empty"] += 1
    
    
    cluster_num = 1
    for x in range(w):
        for y in range(h):
            cell = game_state.map.get_cell(x,y)
            citytile = cell.citytile
            resource = cell.resource
            if cell.has_resource():
                layers_dic["is_empty"][x,y] = 0
                if resource.type == Constants.RESOURCE_TYPES.URANIUM:
                    #layers_dic["is_uranium"][x,y] = 1
                    layers_dic["uranium_amount"][x,y] = resource.amount
                    
                    
                        
                    
                    
                    if(player.researched_uranium()):
                        layers_dic["resource_location"][x,y] += 1
                        layers_dic["can_mine"][x,y] += 1
                        update_4_way(layers_dic["can_mine"] , x,y,w,h,amount=1)
                        set_4_way(layers_dic["is_uranium"] , x,y,w,h,amount=1,center=True)
                        
                        
                if resource.type == Constants.RESOURCE_TYPES.COAL:
                    #layers_dic["is_coal"][x,y] = 1
                    layers_dic["coal_amount"][x,y] = resource.amount
                    
                    if(player.researched_coal()):
                        layers_dic["resource_location"][x,y] += 1
                        update_4_way(layers_dic["is_coal"] , x,y,w,h,amount=1 ,center=True)
                        layers_dic["can_mine"][x,y] +=1
                        set_4_way(layers_dic["can_mine"] , x,y,w,h,amount=1)
                        
                        
                if resource.type == Constants.RESOURCE_TYPES.WOOD:
                    layers_dic["is_wood"][x,y] = 1
                    set_4_way(layers_dic["is_wood"] , x,y,w,h,amount=1)
                    
                    layers_dic["wood_amount"][x,y] = resource.amount
                    layers_dic["can_mine"][x,y] += 1
                    layers_dic["resource_location"][x,y] += 1
                    update_4_way(layers_dic["can_mine"] , x,y,w,h,amount=1)
                    
                    
                clu = check_4_way(layers_dic["resource_clusters"] , x,y,w,h,amount=None , corner = True , center = False )
                if(clu > 0):
                    layers_dic["resource_clusters"][x,y] = clu
                    clusters[clu]["locations"].append(Position(x,y))
                else:
                    layers_dic["resource_clusters"][x,y] = cluster_num 
                    clusters[cluster_num] = {}
                    clusters[cluster_num]["type"] = ClusterType.RESOURCE
                    clusters[cluster_num]["locations"] = []
                    clusters[cluster_num]["locations"].append(Position(x,y))
                    cluster_num +=1
                

            
            
            layers_dic["road_cooldown"][x,y] = cell.road
            
    layers_dic["resource_for_build"] = layers_dic["can_mine"] + (layers_dic['can_mine'] != 0).astype(int) * layers_dic["is_wood"]*10+layers_dic["is_coal"]*2+layers_dic["is_uranium"] 
    
    layers_dic["resource_for_fuel"] = layers_dic["can_mine"] + (layers_dic['can_mine'] != 0).astype(int) * layers_dic["is_wood"]+layers_dic["is_coal"]*2+layers_dic["is_uranium"]*10
        
    
    
    for unit in player.units:
        x,y = unit.pos.x , unit.pos.y
        layers_dic["my_unit"][x,y] = 1
        if unit.type == Constants.UNIT_TYPES.WORKER:
            layers_dic["my_unit_worker"][x,y] = 1
            
        else:
            layers_dic["my_unit_cart"][x,y] = 1
            
        layers_dic["my_unit_worker_can_act"][x,y] = unit.can_act()
        layers_dic["my_unit_worker_cooldown"][x,y] = unit.cooldown
        layers_dic["my_unit_worker_left_space"][x,y] = unit.get_cargo_space_left()
        #layers_dic["my_unit_worker_uranium"][x,y] = unit.cargo.uranium
        #layers_dic["my_unit_worker_coal"][x,y] = unit.cargo.coal
        #layers_dic["my_unit_worker_wood"][x,y] = unit.cargo.wood
        
        

    for unit in opp.units:
        x,y = unit.pos.x , unit.pos.y
        if unit.type == Constants.UNIT_TYPES.WORKER:
            layers_dic["ob_unit_worker"][x,y] = 1
            
        else:
            layers_dic["ob_unit_cart"][x,y] = 1
        
        layers_dic["ob_unit_worker_can_act"][x,y] = unit.can_act()
        layers_dic["ob_unit_worker_cooldown"][x,y] = unit.cooldown
        layers_dic["ob_unit_worker_left_space"][x,y] = unit.get_cargo_space_left()
        #layers_dic["ob_unit_worker_uranium"][x,y] = unit.cargo.uranium
        #layers_dic["ob_unit_worker_coal"][x,y] = unit.cargo.coal
        #layers_dic["ob_unit_worker_wood"][x,y] = unit.cargo.wood
            
            
    for k, city in player.cities.items():
        city_fuel = city.fuel
        city_upkeep = city.get_light_upkeep()
        
        city_can_surv = True if city_fuel > city_upkeep*night_l else False
        city_can_surv2end = True if city_fuel > city_upkeep*night_turns_left else False   
        
        
        city_need_building = 0
        if city_can_surv2end:
            addit_fuel = city_fuel - (city_upkeep*night_turns_left)
            
            for i in [1,2,3]:
                if addit_fuel > (citytile_upkeep-(city_adj_bonus*i))*night_turns_left:
                    city_need_building =  i
                    break
            
                                 

        
        for city_tile in city.citytiles:
            x,y = city_tile.pos.x , city_tile.pos.y
            layers_dic["is_empty"][x,y] = 0
            #layers_dic["my_city_fuel"][x,y] = city.fuel
            layers_dic["my_citytile"][x,y] = 1
            
            
            layers_dic["my_citytile_can_surv"][x,y] = 1 if city_can_surv else 0
            layers_dic["my_citytile_can_surv2end"][x,y] = 1 if city_can_surv2end else 0
            layers_dic["my_city_need_build"][x,y] = city_need_building
            #layers_dic["my_citytile_cool"][x,y] = city_tile.cooldown
            #layers_dic["my_citytile_can_act"][x,y] = city_tile.can_act()
            
            clu = check_4_way(layers_dic["city_clusters"] , x,y,w,h,amount=None , corner = False , center = False )
            if(clu > 0):
                layers_dic["city_clusters"][x,y] = clu
                clusters[clu]["locations"].append(Position(x,y))
            else:
                layers_dic["city_clusters"][x,y] = cluster_num 
                clusters[cluster_num] = {}
                clusters[cluster_num]["type"] = ClusterType.CITY
                clusters[cluster_num]["locations"] = []
                clusters[cluster_num]["locations"].append(Position(x,y))
                cluster_num +=1
            
            
            
    for k, city in opp.cities.items():
        for city_tile in city.citytiles:
            x,y = city_tile.pos.x , city_tile.pos.y
            
            layers_dic["is_empty"][x,y] = 0
            #layers_dic["ob_city_fuel"][x,y] = city.fuel 
            layers_dic["ob_citytile"][x,y] = 1
            #layers_dic["ob_citytile_cool"][x,y] = city_tile.cooldown
            #layers_dic["ob_citytile_can_act"][x,y] = city_tile.can_act()
            
            
            
            
            
    layers_dic['ob_blocks'] += layers_dic['ob_unit_worker'] 
    layers_dic['ob_blocks'] +=  layers_dic['ob_unit_cart'] 
    layers_dic['ob_blocks'] +=  layers_dic['ob_citytile']

    
    
    player_units_count = len(player.units)
    player_citytiles_count = sum([1 for a in player.cities.values() for b in a.citytiles])
    
    #print([b for a in player.cities for b in a])
    
    player_research_points = player.research_points
    

        
    #units_info =[]
    units_info = {}
    units_info["unit"] = []
    units_info["pos"] = []
    units_info["type"] = []
    units_info["units_count"] = player_units_count
    units_info["citytiles_count"] = player_citytiles_count
    units_info["research_points"] = player_research_points
    
    
    
    
    units_info["night_turns_left"] = night_turns_left
    units_info["turns_to_night"] = turns_to_night

    units_info["turns_to_dawn"] = turns_to_dawn

    units_info["is_day_time"] = is_day_time


    for unit in player.units:
        #cnn.append(layers_dic.copy())
        units_info["unit"].append(unit)
        units_info["pos"].append([unit.pos.x,unit.pos.y])
        units_info["type"].append(unit.type)

        
        #units_info.append(unit_info.copy())
        
        #cnn[-1]["unit_pos"][unit.pos.x,unit.pos.y] = 1
        
        
    for k,city in player.cities.items():
        for citytile in city.citytiles:
            #cnn.append(layers_dic.copy())
            units_info["unit"].append(citytile)
            units_info["pos"].append([citytile.pos.x,citytile.pos.y])
            units_info["type"].append("citytile")

            
            #units_info.append(unit_info.copy())
            
            #cnn[-1]["unit_pos"][citytile.pos.x,citytile.pos.y] = 1
            
            
    for x in range(w):
        for y in range(h):
            if layers_dic["is_empty"][x,y] == 1:
                layers_dic["can_build"][x,y] = 1
                
                round_resource = get_4_way(layers_dic["resource_location"] , x,y,w,h,amount=1 ,corner = True)
                round_citytile =  get_4_way(layers_dic["my_citytile"] , x,y,w,h,amount=2)
                round_city_need = get_4_way(layers_dic["my_city_need_build"] , x,y,w,h,amount=1)
                
                
                layers_dic["can_build"][x,y] += round_resource
                layers_dic["can_build"][x,y] += round_citytile
                
                if round_resource < 1 and round_city_need < 1:
                    layers_dic["can_build"][x,y] = 0
                    
                elif round_city_need > 0:
                    
                    if round_city_need/round_citytile == round_citytile:
                        layers_dic["can_build"][x,y] += 10
                    elif round_resource < 1:
                        layers_dic["can_build"][x,y] = 0
                        
                        
    best_count = 3
    clusters_keys = list(clusters.keys())
    for idx in range(len(clusters_keys)):
        for idy in range(idx+1 , len(clusters_keys)):
            
            distances = []
            
            #print(clusters)
            
            clusters1 = list(clusters[clusters_keys[idx]]["locations"])
            clusters2 = list(clusters[clusters_keys[idy]]["locations"])
            
            for pos1 in clusters1:
                for pos2 in clusters2:
                    distances.append({'pos':pos2 , "weight":0 , "distance":pos1.distance_to(pos2) ,"pos2":pos1})
                    
            distances = sorted(distances , key=lambda t:t["distance"])
            
            r=best_count
            if len(distances) < best_count:
                r= len(distances)
            
            closest_dist = math.inf
            closest_path = None
            for dis in distances[:r]:
                path , dist =  get_path(dis['pos'] ,dis['pos2'] ,
                                layers_dic['road_cooldown'],benifit_map = [layers_dic['can_mine']] ,
                                blocks=[layers_dic['ob_citytile']] ,step_cost = 2 )
                
                if dist is not None:       
                    if dist -(dis["weight"]) <= closest_dist:
                        closest_dist = dist -(dis["weight"])
                        closest_path = path
            
            if closest_path is not None:
                for x,y in closest_path:            
                    layers_dic["roads"][x,y] += 1
            
                
                
    layers_dic["can_build"] += layers_dic["roads"]* (layers_dic["can_build"] > 0 ).astype(int)              
            
            
                        
                        
    return  layers_dic ,units_info 



 

# this snippet finds all resources stored on the map and puts them into a list so we can search over them
def find_tiles( tiles ,pos=None,blocks=None):
    resource_tiles = []
    width, height = tiles.shape
    
    block = None
    if blocks is not None:
        block = np.zeros(blocks[0].shape)
        for b in blocks:
            block += b
        
    
    
    for y in range(height):
        for x in range(width):
            d = None
            if pos is not None:
                d = abs(pos.x - x) + abs(pos.y - y)
            if block is not None:
                
                if tiles[x,y] > 0 and block[x,y] == 0:
                    resource_tiles.append({'pos':Position(x,y) , "weight":tiles[x,y] , "distance":d })
            else:
                if tiles[x,y] > 0:
                    resource_tiles.append({'pos':Position(x,y) , "weight":tiles[x,y] , "distance":d})
                    
    if pos is not None:
        resource_tiles = sorted(resource_tiles, key=lambda t: t["distance"]-(t["weight"]/2))
                
                
    return resource_tiles

# the next snippet finds the closest resources that we can mine given position on a map
def find_closest_tile(unit, player , tiles , cnn , benifit_map = None , blocks = None , unit_step = 1 , fast = False , step_cost = 1 ):
    
    pos = unit.pos
    closest_dist = math.inf
    closest_resource_tile = None
    closest_path = None
    
    fast_count = 5
    
    ann = []
    
    block = None
    if blocks is not None:
        block = np.zeros(blocks[0].shape)
        for b in blocks:
            block -= b
    
    
    
    if fast:
        
        new_tiles = []
        
        r = fast_count if len(tiles) > fast_count else len(tiles)
        
        count = 0
        
        for resource_tile in tiles:

            
            
            if block is not None:
                if block[resource_tile['pos'].x,resource_tile['pos'].y] < 0:
                    continue

            
            #dist = resource_tile['pos'].distance_to(pos) - resource_tile['weight']

            new_tiles.append(resource_tile)
            
            if count >= r:
                break
                
            count += 1

        
        #new_tiles = sorted(new_tiles, key=lambda t: t[1])
        
       
        tiles = new_tiles
    
    for resource_tile in tiles:
            
        ann.append(annotate.circle(resource_tile['pos'].x, resource_tile['pos'].y))
        #ann.append(annotate.line(resource_tile['pos'].x, resource_tile['pos'].y, pos.x,pos.y))
        
        path , dist =  get_path(pos ,resource_tile['pos'] ,
                                cnn['road_cooldown'],benifit_map = benifit_map ,
                                blocks=blocks ,step_cost = step_cost )

        #print(unit.id," path dist :",dist ," pos dist :",resource_tile["distance"]," TO:" , resource_tile['pos'].x ,resource_tile['pos'].y)
        #print(unit.id," pos dist :",resource_tile["distance"]," TO:" , resource_tile['pos'].x ,resource_tile['pos'].y)
        #print("weight :",resource_tile["weight"])
        #print("diff :",dist -(resource_tile["weight"]))
        #print("path :",path)
        
        if dist is not None:       
            if dist -(resource_tile["weight"]) <= closest_dist:
                closest_dist = dist -(resource_tile["weight"])
                closest_resource_tile = resource_tile
                closest_path = path
            
            
    if closest_resource_tile is not None:
        ann.append(annotate.x(closest_resource_tile['pos'].x, closest_resource_tile['pos'].y))
        
        for cp in closest_path:
            ann.append(annotate.x(*cp))

            
        
    return closest_resource_tile ,closest_path ,closest_dist,ann 

