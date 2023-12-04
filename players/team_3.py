import random
from queue import PriorityQueue
import math

#maintian memory of actions we did to other players, dictionary
playerID = 0
seat_dictionaryR = {0:[1,2,3], 1:[2,3,4], 2:[3,4,5], 3:[4,5,6], 4:[5,6,7], 5:[6,7,8], 6:[7,8,9], 7:[8,9,0], 8:[9,0,1], 9:[0,1,2]}
seat_dictionaryL = {0:[9,8,7], 1:[0,9,8], 2:[1,0,9], 3:[2,1,0], 4:[3,2,1], 5:[4,3,2], 6:[5,4,3], 7:[6,5,4], 8:[7,6,5], 9:[8,7,6]}
class Player():
    def __init__(self, id, team_num, table_num, seat_num, unique_gossip, color, turns):
        global playerID

        self.id = id
        self.team_num = team_num
        self.table_num = table_num
        self.seat_num = seat_num
        self.color = color
        self.unique_gossip = unique_gossip
        self.gossip_list = [unique_gossip]
        self.group_score = 0
        self.individual_score = 0
        self.turns = 0
        self.totalTurns = turns

        self.priorityGossip = PriorityQueue()
        self.priorityGossip.put(self.unique_gossip)
        
        self.currGossip = unique_gossip #the highest gossip we currently have
        self.prevGossip = unique_gossip #the gossip we start with or the highest gossip we got from the prev table
        self.heardPlayers = [] #players we have heard from
        self.move = False  #are we moving this turn
        self.prevTable = table_num #the table we were just at
        self.emptySeats = [] #the current empty seats, updated every turn at _turn()
        self.uniquePlayerSeed = playerID # we will have 9 distinct player types
        playerID += 1

        self.memory = {} #Dictionary to store all interactions with other players
        self.player_positions = [] #Store received player positions
        self.count = 0

        self.last_direction = "none" #store the last direction we spoke in
        self.last_gossip = 0 #store the last gossip we shared
        self.last_action = "none" #stores our last action
        self.retireCount = {}

        #add in memory (dictionary, key: player id, array: list of actions ("listen/speak", "gossip value")

    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        
        heardPlayers = 0
        self.player_positions = player_positions

        #if we are trying to move, see if we did actually move on the prev turn
        if self.move:
            if self.prevTable != self.table_num:
                self.move = False
                self.prevTable = self.table_num

        #see how many players at the current table we have already heard from
        for player in player_positions:
            player_id = player[0]
            table_num = player[1]
            if table_num == self.table_num:
                if player_id in self.heardPlayers:
                    heardPlayers += 1
        if heardPlayers > 10: #this feature is currently redundant 
            self.move = True 
        


        self.emptySeats = self._emptySeats(player_positions)
        pass

    def get_nearby_players(self, seats, table):
        players = []
        for player in self.player_positions:
            if player[1]==table and player[2] in seats:
                players.append(player[0])
        return players

    def _emptySeats(self, player_positions):
        playerSeats = [[position[1], position[2]] for position in player_positions]
        emptySeats = []
        for table in range(0, 10):
            for seat in range(0, 10):
                currSeat = [table, seat]
                if currSeat not in playerSeats:
                    emptySeats.append([table, seat])
        return emptySeats

    def was_listening(self, direction, players, player_positions):
        playersListening = []
        for i in range(0, len(player_positions)):
            if player_positions[i][0] in players:
                if player_positions[i][1][0]=="listen" and  player_positions[i][1][1]==direction:
                    playersListening.append([player_positions[i][0], True])
                else:
                    playersListening.append([player_positions[i][0], False])
        return playersListening
    
    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):
        if(self.last_action=="talk"):
            gossip=self.last_gossip

            if(self.last_direction=="left"):
                    nearbyPlayers = self.get_nearby_players(seat_dictionaryL[self.seat_num], self.table_num)
                    for player in self.was_listening("right", nearbyPlayers, player_actions):
                        if player[1] == True:
                            value = ("talk", gossip)
                            self.add_to_memory(player[0], value)
            
            elif(self.last_direction=="right"):
                    nearbyPlayers = self.get_nearby_players(seat_dictionaryR[self.seat_num], self.table_num)
                    for player in self.was_listening("left", nearbyPlayers, player_actions):
                        if player[1] == True:
                            value = ("talk", gossip)
                            self.add_to_memory(player[0], value)
            

    def add_to_memory(self, key, value):
        if key!=None:
            if key in self.memory:
                # Check if tuple x already exists in the list for key y
                if value not in self.memory[key]:
                    # If x is not in the list, append it
                    self.memory[key].append(value)
            else:
                # If key y is not in memory, create a new entry with x as the first element of the list
                self.memory[key] = [value]

    def gossip_share(self, players):
        #go thru the queue in order and check if they heard 
        #get random gossip from the top 3 highest gossip
        #maxGossipRange = 2 if self.priorityGossip.qsize() > 2 else 0
        #gossipNum = random.randint(0, maxGossipRange)

        index = self.priorityGossip.qsize()-1
        gossip = self.priorityGossip.queue[index]
        shared = {}

        gossipPQueue = PriorityQueue()
        gossipPQueue.put((gossip,-gossip)) 
        for player in players:
            if(player in self.memory):
                for i in range(0,len(self.memory[player])):
                    if self.memory[player][i][0] == "talk":
                        if self.memory[player][i][1] in shared:
                            currCount = shared[(self.memory[player][i][1])]
                            shared[(self.memory[player][i][1])] = currCount + 1
                        else:
                            shared[(self.memory[player][i][1])] = 1

        while(index!=0):
                index-=1
                gossip = self.priorityGossip.queue[index]
                if gossip in shared:
                    currCount = shared[gossip]
                    gossipPQueue.put((currCount, -gossip))
                else:
                    gossipPQueue.put((0, -gossip))

        retired = True
        while retired:
            if gossipPQueue.qsize() > 0:
                bestGossip = gossipPQueue.get()
                gossip = -bestGossip[1]

                if gossip in self.retireCount:
                    if self.retireCount[gossip] < 4:
                        retired = False
                else:
                    retired = False
            else:
                return self.currGossip

        if gossip in self.retireCount:
            currCount = self.retireCount[gossip]
            self.retireCount[gossip] = currCount + 1
        else:
            self.retireCount[gossip] = 1
                    
        return gossip
                    

    def get_action(self):
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]
        self.turns+=1
        direction = random.randint(0,1)
        gossip = self.currGossip

        #move every x turns or when your new gossip is 20 greater than previous gossip maximum
        if self.turns % (self.uniquePlayerSeed+5) == 0 or (self.currGossip-self.prevGossip) > 19:
            self.prevGossip = self.currGossip
            self.last_action = "move"
            self.last_direction = "none"
            return 'move', self.emptySeats

        # talk
        if self.currGossip/180 > random.random():

            # left
            if direction == 0:
                
                nearbyPlayers = self.get_nearby_players(seat_dictionaryL[self.seat_num], self.table_num)
                gossip = self.gossip_share(nearbyPlayers)
                value = ("talk", gossip)
                self.last_action = "talk"
                self.last_direction = "left"
                self.last_gossip = gossip 
                #self.add_to_memory(key, value)

                return 'talk', 'left', gossip
            
            # right
            else:

                nearbyPlayers = self.get_nearby_players(seat_dictionaryR[self.seat_num], self.table_num)
                gossip = self.gossip_share(nearbyPlayers)
                value = ("talk", gossip)
                #self.add_to_memory(key, value)
                self.last_action = "talk"
                self.last_direction = "right"
                self.last_gossip = gossip 

                return 'talk', 'right', gossip
        
        # listen
        else:
            # left
            self.count+=1
            if direction == 0:
                self.last_action = "listen"
                self.last_direction = "left"
                return 'listen', 'left'
            # right
            else:
                self.last_action = "listen"
                self.last_direction = "right"
                return 'listen', 'right'
    
    def feedback(self, feedback):
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        self.gossip_list.append(gossip_item)

        #Save to memory
        value = ( "listen", gossip_item)  
        self.add_to_memory(gossip_talker, value)

        self.priorityGossip.put(gossip_item)
        self.heardPlayers.append(gossip_talker)
        self.currGossip = self.priorityGossip.queue[self.priorityGossip.qsize()-1]

        pass
    
    def decide_to_talk(self, gossip): #decide whether to talk or listen 
        threshold = 40
        heuristic = gossip + .125*self.turns
        if heuristic > threshold:
            return True
        return False
    

