import random
from queue import PriorityQueue

class Player():
    def __init__(self, id, team_num, table_num, seat_num, unique_gossip, color, turns):
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

        self.priorityGossip = PriorityQueue()
        self.priorityGossip.put(self.unique_gossip)
        
        self.currGossip = unique_gossip #the highest gossip we currently have
        self.prevGossip = unique_gossip #the gossip we start with or the highest gossip we got from the prev table
        self.heardPlayers = [] #players we have heard from
        self.move = False  #are we moving this turn
        self.prevTable = table_num #the table we were just at
        self.emptySeats = [] #the current empty seats, updated every turn at observe_before_turn()
        self.uniquePlayerSeed = random.randint(1, 9) # we will have 9 distinct player types


    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        heardPlayers = 0

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
        if heardPlayers > 5: 
            self.move = True

        self.emptySeats = self._emptySeats(player_positions)
        pass

    def _emptySeats(self, player_positions):
        playerSeats = [[position[1], position[2]] for position in player_positions]
        emptySeats = []
        for table in range(0, 10):
            for seat in range(0, 10):
                currSeat = [table, seat]
                if currSeat not in playerSeats:
                    emptySeats.append([table, seat])
        return emptySeats

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):
        pass

    def get_action(self):
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]
        self.turns+=1
        direction = random.randint(0, 1)

        #move every 5 turns or when your new gossip is 20 greater than previous gossip maximum
        if self.turns % (self.uniquePlayerSeed+5) == 0 or (self.currGossip-self.prevGossip) > 19 or self.move:
            self.prevGossip = self.currGossip
            return 'move', self.emptySeats

        # talk
        if self.currGossip/90 > random.random():

            #get random gossip from the top 3 highest gossip
            maxGossipRange = 2 if self.priorityGossip.qsize() > 2 else 0
            gossipNum = random.randint(0, maxGossipRange)
            gossip = self.priorityGossip.queue[gossipNum]

            # left
            if direction == 0:
                return 'talk', 'left', gossip
            # right
            else:
                return 'talk', 'right', gossip
        
        # listen
        else:
            # left
            if direction == 0:
                return 'listen', 'left'
            # right
            else:
                return 'listen', 'right'
    
    def feedback(self, feedback):
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        self.gossip_list.append(gossip_item)
        self.priorityGossip.put(gossip_item)
        self.heardPlayers.append(gossip_talker)
        self.currGossip = self.priorityGossip.queue[0]

        pass
    