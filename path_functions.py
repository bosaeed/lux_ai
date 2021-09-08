from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import numpy as np
import random
from game_functions import *
from map_functions import *
import settings #import settings.cashed_roads ,settings.current_turn
from settings import ClusterType
import sys 


import collections

#aaaaa="zzzzzzzzzzzzzzzzzzzzzz"

class RoadInfo:
    
    def __init__(self,before_point , weight ,benifit=0,block_weight=0, is_end = False):
        self.before_point = before_point
        self.weight = weight
        self.is_end = is_end
        self.benifit = benifit
        self.block_weight = block_weight
        
        
        
        
    def __str__ (self):
        return f"B: {self.before_point} W: {self.weight} block: {self.benifit} end: {self.is_end} "
        
def get_road_weight(end_point , roads):
    w=0
    
    x,y = end_point.x , end_point.y
    
    while roads[x][y].before_point != None:
        
        w += roads[x][y].block_weight
        x,y = roads[x][y].before_point
        
    return w
        
        




def get_path(start_pos ,end_pos ,cost_map , benifit_map = None ,  blocks=None ,step_cost =1 ,dist_thers = 6 ):
    
    
    road_max_live = 100
    
    
    
    fast_way = True
    
    check_cash = False if len(settings.cashed_roads) < 1 or (end_pos.x,end_pos.y) not in settings.cashed_roads  else True
    
    found_cash = False
    
    height ,width  = cost_map.shape
    
    roads = [[None for _ in range(width)] for _ in range(height)]
    
    paths_count = 2
    
    path_found = False


    cycles_after_find = 0
    
    paths = []
    
    
    dist = 0
    block = None
    if blocks is not None:
        block = np.zeros(blocks[0].shape)
        for b in blocks:
            block -= b
            
    benifit = None
    if benifit_map is not None:
        benifit = np.zeros(blocks[0].shape)
        for b in benifit_map:
            benifit += b
            
            
    queue = collections.deque([[(start_pos.x,start_pos.y)]])
    roads[start_pos.x][start_pos.y] = RoadInfo(before_point = None ,weight = 0,
                                               benifit=0 ,is_end =start_pos.equals(end_pos))
    
    #print("strat pos:" ,(start_pos.x,start_pos.y) , "end pos:" ,(end_pos.x,end_pos.y))
    
    
    if fast_way:
        
        way = 1
        if start_pos.x < end_pos.x:
            way = -1
            
            
        if start_pos.x != end_pos.x:
            path = [(start_pos.x, start_pos.y)]
            
            
            
            y2 = start_pos.y
            
            
            
            for x2 in range(start_pos.x+way , end_pos.x , way):
                
                
                before_w =  roads[x2 - (way)][y2].weight
                before_b =  roads[x2 - (way)][y2].benifit
                
                w = 0
                if step_cost > cost_map[x2,y2] and not Position(x2, y2).equals(end_pos):
                    w = step_cost - cost_map[x2,y2] +before_w
                else:
                    w=1+before_w
                    
                b = 0
                if benifit is not None:
                    b = benifit[x2,y2] +before_b
                    
                    
                if block is not None:
                    if block[x2,y2] >= 0:
                        path.append((x2, y2))
                        
                        
                        roads[x2][y2] = RoadInfo(before_point = (x2 - (way), y2) , weight = w,
                                                 benifit=b ,is_end =Position(x2, y2).equals(end_pos))
                        
                    else:
                        break
                        #seen.add((x2, y2))
                
                else:
                    
                    path.append((x2, y2))
                    
                    
                    roads[x2][y2] = RoadInfo(before_point = (x2 - (way), y2) ,  weight = w,
                                             benifit=b ,is_end =Position(x2, y2).equals(end_pos))
                
                
            queue.appendleft(path)
            
        way = 1
        if start_pos.y < end_pos.y:
            way = -1
            
            
        if start_pos.y != end_pos.y:
            path = [(start_pos.x, start_pos.y)]
            x2 = start_pos.x
            
            
            
            for y2 in range(start_pos.y+way , end_pos.y , way):
                
                before_w =  roads[x2 ][y2- (way)].weight
                before_b =  roads[x2 ][y2- (way)].benifit
                
                w = 0
                if step_cost > cost_map[x2,y2] and not Position(x2, y2).equals(end_pos):
                    block_w = step_cost - cost_map[x2,y2]
                else:
                    block_w=1
                    
                w = block_w + before_w
                    
                b = 0
                if benifit is not None:
                    b = benifit[x2,y2] +before_b
                    
                    
                if block is not None:
                    if block[x2,y2] >= 0:
                        path.append((x2, y2))
                        
                        
                        roads[x2][y2] = RoadInfo(before_point = (x2 , y2- (way)) , weight = w,
                                                 benifit=b ,is_end =Position(x2, y2).equals(end_pos))
                    
                    else:
                        break
                
                else:
                    
                    path.append((x2, y2))
                    
                    
                    roads[x2][y2] = RoadInfo(before_point = (x2 , y2- (way)) ,  weight = w,
                                             benifit=b ,is_end =Position(x2, y2).equals(end_pos))
                
                
            queue.appendleft(path)
            
            
        
        
        
        
    
    while queue:
        #print(queue)
        if path_found :
            cycles_after_find += 1
        
        
        path = queue.popleft()
        x, y = path[-1]
        
        #print(path)
        if roads[x][y].is_end :
            paths.append(path)
            path_found =True
            #print(path)
            
            if len(paths) >= paths_count or roads[x][y].weight < dist_thers or cycles_after_find > 20  or found_cash:
                
                break
                
            continue
        
        
        
            
        before_w =  roads[x][y].weight
        before_b =  roads[x][y].benifit
        for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
                           
            if 0 <= x2 < height and 0 <= y2 < width :# and (x2, y2) not in seen:
                    
                w = 0
                block_w = 0
                if step_cost > cost_map[x2,y2] and not Position(x2, y2).equals(end_pos):
                    block_w = step_cost - cost_map[x2,y2]
                else:
                    block_w=1
                    
                w = block_w + before_w
                    
                    
                    
                    
                    
                b = 0
                if benifit is not None:
                    b = benifit[x2,y2] +before_b
                
                
                if check_cash :
                    if (x2, y2) in settings.cashed_roads[(end_pos.x,end_pos.y)]:
                        
                        no_dup = True
                        
                        #print("current path \n" ,path)

                        #print("cashed \n" ,settings.cashed_roads[(end_pos.x,end_pos.y)])

                        path_list = settings.cashed_roads[(end_pos.x,end_pos.y)][(x2, y2)]["paths"]
                        
                        #print("path list \n" ,path_list)
                        
                        
                        road_live = True if settings.current_turn - settings.cashed_roads[(end_pos.x,end_pos.y)][(x2, y2)]["turn"]  <road_max_live else False
                        
                        #if not road_live:
                        #print("settings.current_turn :",settings.current_turn ,"road_turn :",settings.cashed_roads[(end_pos.x,end_pos.y)][(x2, y2)]["turn"])
                        
                        found_cash = False
                        
                        for pa in path:
                            if pa in path_list:
                                no_dup = False
                        
                        if no_dup:

                            before_w2 =  before_w
                            before_b2 =  before_b


                            

                            fast_p = []

                            #print("start : ",(start_pos.x, start_pos.y))
                            #print("connect : ",(x2, y2))
                            #print("end : ",(end_pos.x, end_pos.y))
                            
                            
                            break_d = False if road_live else True
                            
                            
                            
                            
                            
                            
                            for x3,y3 in path_list:

                                if block is not None:
                                    if block[x3,y3] < 0:
                                        break_d = True
                                        
                                        break
                                        
                            
                                        
                                        
                                        
                            if not break_d:
                                #print("b : ",path)
                                path += path_list
                                #print("a : ",path)


                                #print("path comb :\n",path)


                                queue.appendleft(path)
                                found_cash = True
                                
                                before_p = path[0]
                                
                                #print("strat Road :\n" , roads[path[0][0]][path[0][1]])
                                
                                for x3,y3 in path[1:]:


                                    w2 = 0

                                    block_w2 = 0
                                    if step_cost > cost_map[x3,y3] and not Position(x3, y3).equals(end_pos):
                                        block_w2 = step_cost - cost_map[x3,y3] 
                                    else:
                                        block_w2=1

                                    w2 = block_w2 + before_w2




                                    b2 = 0
                                    if benifit is not None:
                                        b2 = benifit[x2,y2] +before_b2

                        
                                    roads[x3][y3] = RoadInfo(before_point = before_p , weight = w2,
                                                         benifit=b2 ,is_end =Position(x3, y3).equals(end_pos) ,block_weight = block_w2)
                            
                                    #print(x3,y3 , roads[x3][y3])

                                    #fast_p.append((x3,y3))

                                    before_w2 =  w2
                                    before_b2 =  b2

                                    before_p = (x3, y3)
                                    
                            else:
                                
                                #print(settings.cashed_roads[(end_pos.x,end_pos.y)])
                                settings.cashed_roads[(end_pos.x,end_pos.y)].pop((x2, y2))
                                #print(settings.cashed_roads[(end_pos.x,end_pos.y)])

                                
                                break

                
                
                
                
                if roads[x2][y2] is not None  :
                    if roads[x2][y2].before_point != (x2,y2):
                        continue
                    
                    
                    if w < roads[x2][y2].weight:
                        queue.append(path + [(x2, y2)])
                        roads[x2][y2].weight = w
                        roads[x2][y2].before_point = (x, y)
                        roads[x2][y2].block_weight = block_w
                        
                    if w == roads[x2][y2].weight and b> roads[x2][y2].benifit:
                        queue.append(path + [(x2, y2)])
                        roads[x2][y2].weight = w
                        roads[x2][y2].before_point = (x, y)
                        roads[x2][y2].block_weight = block_w
                    
                    
                
                elif block is not None:
                    if block[x2,y2] >= 0:
                        queue.append(path + [(x2, y2)])
                        
                        
                        roads[x2][y2] = RoadInfo(before_point = (x, y) , weight = w,
                                                 benifit=b ,is_end =Position(x2, y2).equals(end_pos) ,block_weight = block_w)
                        #seen.add((x2, y2))
                
                else:
                    queue.append(path + [(x2, y2)])
       
                    
                    
                    roads[x2][y2] = RoadInfo(before_point = (x, y) ,  weight = w,
                                             benifit=b ,is_end =Position(x2, y2).equals(end_pos) ,block_weight = block_w)
                    #seen.add((x2, y2))
    if roads[end_pos.x][end_pos.y] is None:   
        return None ,None
    
    path = []
    weight = 0
    
    x , y = end_pos.x ,end_pos.y
    weight = roads[x][y].weight
    
    #print("end point :",x , y)
    #print("start point :",start_pos.x , start_pos.y)
    path = collections.deque([])
    while True:
        
        
        #print("before it :",roads[x][y].before_point)
        path.appendleft((x,y))
        
        
        #print(path)
        if Position(x,y).equals(start_pos):
            break
        
        if roads[x][y].before_point in path:
            print("wrong loop")
            sys.exit(1)

        
        
        x , y = roads[x][y].before_point
        
        
        
    #print("cycles_after_find :",cycles_after_find , "found paths :",len(paths))
    
    path = list(path)
    
    if (end_pos.x,end_pos.y) not in settings.cashed_roads:
        
        settings.cashed_roads[(end_pos.x,end_pos.y)] = {}
        
    
    for i in range(len(path)-1):
        
        if path[i] not in settings.cashed_roads[(end_pos.x,end_pos.y)]:
            settings.cashed_roads[(end_pos.x,end_pos.y)][path[i]] = {}
            settings.cashed_roads[(end_pos.x,end_pos.y)][path[i]]["paths"] = {}
            settings.cashed_roads[(end_pos.x,end_pos.y)][path[i]]["turn"] = settings.current_turn
            
        settings.cashed_roads[(end_pos.x,end_pos.y)][path[i]]["paths"] = path[i:].copy()
        #settings.cashed_roads[(end_pos.x,end_pos.y)][path[i]]["turn"] = settings.current_turn
    
    
    #print(settings.cashed_roads)
    
    return path , weight 
        
    

