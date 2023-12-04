import random
import math

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
        self.turn_num = -1
        self.player_positions = []
        self.player_actions = []
        self.turns = turns


    def observe_before_turn(self, player_positions):
        '''At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move'''
        self.player_positions = player_positions # list of lists, each of which is [player_id, table_num, seat_num]

    def observe_after_turn(self, player_actions):
        '''At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn) did (i.e., talked/listened in what direction, or moved)'''
        self.player_actions = player_actions # list of lists, each of which is [player_id, action_type, direction] (CCW = right, CW = left)

    def _get_command(self):
        '''Returns 'talk', 'listen', or 'move'.'''
        # TODO: Change default behavior seen below to specifications in Brainstorming doc (Stephen)
        if random.random() < 0.12:
            return 'move'
        
        talk_or_listen_prob = random.random()
        highest_gossip_prob = max(self.gossip_list) / 90 

        if self.turn_num < self.turns/2: 
            if talk_or_listen_prob <= highest_gossip_prob:
                return 'talk'
            else:
                return 'listen'
        else:

            if talk_or_listen_prob <= 0.5: 
                return 'talk'
            else:
                return 'listen'
    
    def _get_direction(self, command):
        '''Returns 'left' or 'right' for the given command (which must be 'talk' or 'listen').'''
        if self.turn_num % 2 == 0:
            if command == 'talk':
                return 'right'
            elif command == 'listen':
                return 'left'
        else:
            if command == 'talk':
                return 'left'
            elif command == 'listen':
                return 'right'
    
    def _get_gossip(self):
        '''Returns the gossip number we want to say.'''
        # desired_gossip = 90 - 89 / self.turns * self.turn_num  # linear decay  1700
        # desired_gossip = 90 ** (1 - self.turn_num / self.turns)  # exponential decay  800
        # desired_gossip = 91 - 90 ** (self.turn_num / self.turns)  # inverse exponential decay  1700
        # return min(self.gossip_list, key=lambda gossip: abs(gossip - desired_gossip))
        # return random.choices(self.gossip_list, weights=[1 / (abs(gossip - desired_gossip) + 1) + 1 for gossip in self.gossip_list], k=1)[0]  2399 3527
        # return max(self.gossip_list)  # choose max  300
        # return self.unique_gossip  # choose initial  2100
        return random.choice(self.gossip_list)  # choose random  2374  4038
    
    def _get_seats(self):
        '''Returns an ordered list of empty seats to move to in the form [[table1, seat1], [table2, seat2], ...].'''
        # TODO: Change default behavior seen below to specifications in Brainstorming doc (Cristopher)
        OccupiedSeats = [[item[1], item[2]] for item in self.player_positions]
        EmptySeats = []
        for table_num in range(10):
            for seat_num in range(10):
                seat = [table_num, seat_num]
                if seat not in OccupiedSeats:
                    EmptySeats.append([table_num, seat_num])

        random.shuffle(EmptySeats) #Shuffling the list of empty seats to randomize the order of the seats to remove bias.

        #Sorting based on the seats with neighbors
        temp1 =[]
        temp2 =[]
        temp3 =[]
        temp4 =[]
        temp5 =[]
        temp6 =[]
        for seat in EmptySeats:
            neighbors = []
            #print("seat:", seat)
            for i in range(-3, 4): # range for 3 neighbors on each side   
                if [seat[0], (seat[1] + i) % 10] in OccupiedSeats and (seat[1] + i) % 10 in range(0, 10) and i != 0:
                    neighbors.append([seat[0], (seat[1] + i) % 10])
            neighbors = sorted(neighbors , key=lambda x: x[1])
            #print("neighbor:", neighbors)
            neighborSeats = [item[1] for item in neighbors]
            if len(neighborSeats) >=5:
                if len(neighborSeats) == 6:
                    temp1.append(seat)
                else:
                    temp2.append(seat)
            elif len(neighbors) >= 3:
                if range(seat[1], max(neighborSeats) + 1) in neighborSeats or range(min(neighborSeats), seat[1] + 1) in neighborSeats:
                    temp3.append(seat)
                else:
                    temp4.append(seat) 
            elif len(neighbors)  >= 1:
                if range(seat[1], max(neighborSeats) + 1) in neighborSeats or range(min(neighborSeats), seat[1] + 1) in neighborSeats:
                    temp5.append(seat)
                else:
                    temp6.append(seat)
        #print("Done")

        priority_EmptySeats = temp1 + temp2 + temp3 + temp4 + temp5 + temp6
        #print("Empty Seats: ", EmptySeats)
        #print("Priority EmptySeats: ", priority_EmptySeats)

        return priority_EmptySeats


    def get_action(self):
        '''
        Returns one of the following forms:
        - 'talk', 'left', <gossip_number>
        - 'talk', 'right', <gossip_number>
        - 'listen', 'left'
        - 'listen', 'right'
        - 'move', priority_list: [[table number, seat number] ...]
        '''
        self.turn_num += 1
        command = self._get_command()
        if command == 'talk':
            return command, self._get_direction(command), self._get_gossip()
        elif command == 'listen':
            return command, self._get_direction(command)
        elif command == 'move':
            return command, self._get_seats()
    
    def feedback(self, feedback):
        '''Respond to feedback from a person we talked to.'''
        
        list = [[item[0], item[1], item[2]] for item in self.player_positions if item[1] == self.table_num]
        OccupiedSeatsAtTable = [[item[1], item[2]] for item in list]
        selfActionAtTable = []
        for item in self.player_actions:
            if item[0] == self.id:
                selfActionAtTable = [item[0], item[1][0], item[1][1]] 

        selfPosition = [self.table_num, self.seat_num]
        CurrentNeighbors = []
        CurrentNeighbors2 = []


        for i in range(-3, 4):
            if [selfPosition[0], (selfPosition[1] + i) % 10] in OccupiedSeatsAtTable and (selfPosition[1] + i) % 10 in range(0, 10) and i != 0:
                CurrentNeighbors.append([selfPosition[0], (selfPosition[1] + i) % 10])
        
        for cell in list:
            sub_cell = cell[1:]
            if sub_cell in CurrentNeighbors:
                CurrentNeighbors2.append(cell)
    
        if feedback and feedback[0].startswith('Shake Head'):
            if selfActionAtTable and selfActionAtTable[2] == "left":
                # print("Left Player Shook Head, should turn right")
                return 'right'
            else:
                # print("Right Player Shook Head, should turn left")
                return 'left'
        # print("feedback: ", feedback)
        # print("selfPosition: ", selfPosition)
        # print("OccupiedSeatsAtTable: ", OccupiedSeatsAtTable)
        # print("CurrentNeighbors2: ", CurrentNeighbors2)
        # print("CurrentActionaAtTable: ", selfActionAtTable)
        # print("Done")


        pass


   

    def get_gossip(self, gossip_item, gossip_talker):
        '''Respond to gossip told to us.'''
        if gossip_item not in self.gossip_list:
            self.gossip_list.append(gossip_item)
