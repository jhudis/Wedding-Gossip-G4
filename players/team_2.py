import random
import heapq

class Player():
    def __init__(self, id, team_num, table_num, seat_num, unique_gossip, color):
        self.id = id
        self.team_num = team_num
        self.table_num = table_num
        self.seat_num = seat_num
        self.color = color
        self.unique_gossip = unique_gossip
        self.gossip_list = [unique_gossip]
        self.group_score = 0
        self.individual_score = 0
        #dictionary template -> dict3 = {'gossip_shared': '15,16,77', 'gossip_score': 55}
        dictionary_temp = {'gossip_shared': [], 'gossip_score': id}
        self.gossip_pq = []
        heapq.heappush(self.gossip_pq, (dictionary_temp['gossip_score'], dictionary_temp))
        #initialize a pq for gossip initlaized with just your own gossip shared with nobody 




    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        pass

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):
        my_action = "talk"
        for action in player_actions:
            player_id = action[0]
            actual_action = action[1][1]
            success = action[1][2] # not super sure on this one 
            if player_id == self.id: 
                my_action = actual_action
                break 
        if my_action == 'talk':
            #see who we shared w 
            for action in player_actions:
                player_id = action[0]
                actual_action = action[1][1]
                success = action[1][2] # not super sure on this one
                #update those spoken to 
        if my_action == 'listen':
            #save to pq 
            for action in player_actions:
                player_id = action[0]
                actual_action = action[1][1]
                success = action[1][2] # not super sure on this one
                d_temp = {'gossip_shared': [self.id], 'gossip_score': player_id}
                heapq.heappush(self.gossip_pq, (d_temp['gossip_score'], d_temp))




        #if you talked, add whichever success listens to set for that specific gossip 

        #if you listen, add that new gossip to your pq 

    def get_action(self):
        #get heuristic of your current pq 
        #and status of players in radius around you 
        #use a ratio to dictate the optimal split of the # of listners, talkers, and movers


        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]

        action_type = random.randint(0, 2)

        # talk
        if action_type == 0:
            direction = random.randint(0, 1)
            gossip = random.choice(self.gossip_list)
            # left
            if direction == 0:
                return 'talk', 'left', gossip
            # right
            else:
                return 'talk', 'right', gossip
        
        # listen
        elif action_type == 1:
            direction = random.randint(0, 1)
            # left
            if direction == 0:
                return 'listen', 'left'
            # right
            else:
                return 'listen', 'right'

        # move
        else:
            table1 = random.randint(0, 9)
            seat1 = random.randint(0, 9)

            table2 = random.randint(0, 9)
            while table2 == table1:
                table2 = random.randint(0, 9)

            seat2 = random.randint(0, 9)

            return 'move', [[table1, seat1], [table2, seat2]]
    
    def feedback(self, feedback):
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        pass