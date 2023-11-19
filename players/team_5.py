import random

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


        # each tuple stores the following for seat 'seat_num' at table 'table_num'
        # 0 index - last observed action done by the player (initialized to None) - can be 'speak' or 'listen'
        # 1 index - direction of the action represented in action 0 (initialized to None) - can be 'left' or right
        # 2 index - player_id of last observed player at the seat (initialized to None)
        # 3 index - time_stamp of last observation (initialized to -1)
        self._curr_state = {table_num: {seat_num: (None, None, None, -1) for seat_num in range(10)} for table_num in range(10)}

        # update it at every step! (currently updating it when the 'observe_after_turn' is called)
        self.time_stamp = 0

        # a hash mapping player_ids to where they are situated on the board
        # each player_id is mapped to (table_num, seat_num)
        # initialized to (None, None)
        self.player_seat_map = {p_id: (None, None) for i in range(90)}

        # action_to_num - to convert action into numerical value for model training purposes
        # can change the values to larger difference if this affects the model training
        self.action_to_num = {('speak', 'left'): 1,
                              ('speak', 'right'): 2
                              ('listen', 'left'): 3
                              ('listen', 'right'): 4}


    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        """
            player_positions - 3-dimensional tuple: (player_id, table_num, seat_num)
        """

        print(f'Before:- team_num - {self.team_num}, table_num - {self.table_num}, seat_num - {self.seat_num} || player_positions - {player_positions}')
        for player_info in player_positions:
            # update the seating into the self._curr_state variable
            self._curr_state[player_info[1]][player_info[2]][2] = player_info[0]
            
            # also update the self.player_seat_map for future reference
            self.player_seat_map[player_info[0]] = (player_info[1], player_info[2])


    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):
        """
            player_actions - 2-dimensional list: [player_id, [player_action[0], player_action[1]]]. Where player_action[0] can be 'talk' or 'listen', and player_action[1] can be 'left' or 'right'
        """

        # update the global timer
        self.time_stamp += 1
        print(f'After:- team_num - {self.team_num}, table_num - {self.table_num}, seat_num - {self.seat_num} || player_positions - {player_positions}')
        for player_info in player_positions:
            # Get the seat info for this player
            curr_table_num, curr_seat_num = self.player_seat_map[player]

            # update the self._curr_state variable with the current observed information
            self._curr_state[curr_table_num][curr_seat_num][0] = player_info[1][0]
            self._curr_state[curr_table_num][curr_seat_num][1] = player_info[1][1]

    def get_action(self):
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
