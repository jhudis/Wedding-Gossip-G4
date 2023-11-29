import random

class Player():
    def __init__(self, id, team_num, table_num, seat_num, unique_gossip, color, turns):
        self.id = id
        self.team_num = team_num
        self.table_num = table_num # maintained by simulator
        self.seat_num = seat_num # maintained by simulator
        self.color = color
        self.unique_gossip = unique_gossip
        self.gossip_list = [unique_gossip] # maintained by simulator
        self.group_score = 0
        self.individual_score = 0
        self.turns = turns

        self._mylastact = '' # my last action
        self._dest_table = -1 # destination table number
        self._dest_seat = -1 # destination seat number

        self._rndCnt = 0 # round counter
        self._probAtndGsp = [[0]*91 for atnd in range(90)] # probability of attendee (0-89) having gossip (1-90)
        self._tbsts = [[-1]*10 for table in range(10)] # real-time seating info of each table; -1 if empty

        self._lastrndnews = None # player actions in my table in the last round
        self._lrntnewgsp = -1 # whether learnt new gossip in the last round
        self._lrntnewgspSrc = -1 # source of the new gossip learnt in the last round

        self._nextacts = [] # next actions to take

        print(self.turns)

    def _pick_next_seat(self):
        pass


    def observe_before_turn(self, player_positions):
        '''
        At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
        
        player_positions (list[list[int]]): [[player_id, table_num, seat_num]]
        '''
        self._rndCnt += 1
        self._tbsts = [[-1]*10 for table in range(10)] # reset seating info
        for player_id, table_num, seat_num in player_positions:
            self._tbsts[table_num][seat_num] = player_id

    def observe_after_turn(self, player_actions):
        '''
        At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn) did (i.e., talked/listened and in what direction)

        player_actions (list[list[str]]): [[player_id, talk/listen, left/right]]
        '''
        self._lastrndnews = player_actions
        if self._mylastact == 'listen':
            if self._lrntnewgsp > 0:
                src_id = self._lrntnewgspSrc
                self._tbsts[self.table_num].index(src_id)

    def get_action(self):
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]
        self._lrntnewgsp = -1
        self._lrntnewgspSrc = -1
        if self._rndCnt == 1:
            if random.random() < (self.unique_gossip/90)**3:
                self._mylastact = 'talk'
                return 'talk', 'right', self.unique_gossip
            else:
                self._mylastact = 'listen'
                return 'listen', 'left'
        
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

            return 'move', [[table1, seat1], [table2, seat2], [table2, seat2], [table2, seat2], [table2, seat2], [table2, seat2],\
                            [table2, seat2], [table2, seat2], [table2, seat2], [table2, seat2], [table2, seat2], [table2, seat2]]
    
    def feedback(self, feedback):
        listener_cnt = len(feedback)
        if random.random() > listener_cnt/3:
            self._nextacts

    def get_gossip(self, gossip_item, gossip_talker):
        self._lrntnewgsp = gossip_item
        self._lrntnewgspSrc = gossip_talker
