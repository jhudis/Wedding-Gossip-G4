import random

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
        self.turns_num = turns

        self.curr_turn = 0
        self.hottest_goss = unique_gossip
        self.empty_seats = []

    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        self._get_empty_seats(player_positions)

    def _get_empty_seats(self, player_positions):
        self.empty_seats.clear()
        occupied = {(t, s) for _, t, s in player_positions}
        for t in range(10):
            for s in range(10):
                if (t, s) not in occupied:
                    self.empty_seats.append([t, s])

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened and in what direction)
    def observe_after_turn(self, player_actions):
        pass

    def get_action(self):
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]

        choice = random.random()
        self.curr_turn += 1

        # talk
        if choice < self.hottest_goss / 90 * .9:
            direction = 'right' if self.curr_turn % 2 else 'left'
            return 'talk', direction, self.hottest_goss
        # listen
        elif choice < .9:
            direction = 'left' if self.curr_turn % 2 else 'right'
            return 'listen', direction
        # move
        else:
            random.shuffle(self.empty_seats)
            return 'move', self.empty_seats
    
    def feedback(self, feedback):
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        self.hottest_goss = max(self.hottest_goss, gossip_item)
