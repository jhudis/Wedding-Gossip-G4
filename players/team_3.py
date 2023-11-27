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
        self.currGossip = unique_gossip #the highest gossip we currently have
        self.prevGossip = unique_gossip #the gossip we start with or the highest gossip we got from the prev table
        self.heardPlayers = [] 
        self.move = False
        self.prevTable = table_num


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
        if heardPlayers > 6: 
            self.move = True
        pass

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
        action_type = self.turns%2

        #move every 5 turns or when ur gossip is 20 greater than previous gossip maximum
        if self.turns % 5 == 0 or (self.currGossip-self.prevGossip) > 19 or self.move:
            self.prevGossip = self.currGossip
            table1 = random.randint(0, 9)
            seat1 = random.randint(0, 9)

            table2 = random.randint(0, 9)
            while table2 == table1:
                table2 = random.randint(0, 9)

            seat2 = random.randint(0, 9)
            
            return 'move', [[table1, seat1], [table2, seat2]]


        # talk
        if self.currGossip>50:
            direction = random.randint(0, 1)
            # left
            if action_type == 0:
                return 'talk', 'left', self.currGossip
            # right
            else:
                return 'talk', 'right', self.currGossip
        
        # listen
        else:
            direction = random.randint(0, 1)
            # left
            if action_type == 0:
                return 'listen', 'left'
            # right
            else:
                return 'listen', 'right'

        # move
        # else:
        #     table1 = random.randint(0, 9)
        #     seat1 = random.randint(0, 9)

        #     table2 = random.randint(0, 9)
        #     while table2 == table1:
        #         table2 = random.randint(0, 9)

        #     seat2 = random.randint(0, 9)

        #     return 'move', [[table1, seat1], [table2, seat2]]
    
    def feedback(self, feedback):
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        self.gossip_list.append(gossip_item)
        self.priorityGossip.put(gossip_item)
        self.heardPlayers.append(gossip_talker)
        self.currGossip = self.priorityGossip.queue[0]

        pass
    