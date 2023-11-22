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


    def observe_before_turn(self, player_positions):
        '''At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move'''
        pass

    def observe_after_turn(self, player_actions):
        '''At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn) did (i.e., talked/listened in what direction, or moved)'''
        pass

    def _get_command(self):
        '''Returns 'talk', 'listen', or 'move'.'''
        # TODO: Change default behavior seen below to specifications in Brainstorming doc (Stephen)
        if random.random() < 0.5:
            return 'move'
        elif max(self.gossip_list) > 45:
            return 'talk'
        else:
            return 'listen'
    
    def _get_direction(self, command):
        '''Returns 'left' or 'right' for the given command (which must be 'talk' or 'listen').'''
        # TODO: Change default behavior seen below to specifications in Brainstorming doc (Justin)
        return ['left', 'right'][random.randint(0, 1)]
    
    def _get_gossip(self):
        '''Returns the gossip number we want to say.'''
        return max(self.gossip_list)
    
    def _get_seats(self):
        '''Returns an ordered list of empty seats to move to in the form [[table1, seat1], [table2, seat2], ...].'''
        # TODO: Change default behavior seen below to specifications in Brainstorming doc (Christopher)
        table1 = random.randint(0, 9)
        table2 = random.randint(0, 9)
        while table2 == table1:
            table2 = random.randint(0, 9)
        seat1 = random.randint(0, 9)
        seat2 = random.randint(0, 9)
        return [[table1, seat1], [table2, seat2]]

    def get_action(self):
        '''
        Returns one of the following forms:
        - 'talk', 'left', <gossip_number>
        - 'talk', 'right', <gossip_number>
        - 'listen', 'left'
        - 'listen', 'right'
        - 'move', priority_list: [[table number, seat number] ...]
        '''
        command = self._get_command()
        if command == 'talk':
            return command, self._get_direction(command), self._get_gossip()
        elif command == 'listen':
            return command, self._get_direction(command)
        elif command == 'move':
            return command, self._get_seats()
    
    def feedback(self, feedback):
        '''Respond to feedback from a person we talked to.'''
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        '''Respond to gossip told to us.'''
        pass
