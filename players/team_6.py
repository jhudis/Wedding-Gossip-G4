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
        # store how many times we listen to each player
        self.gossip_talkers = {}
        # store how many times we hear each gossip
        self.gossip_items = {}
        # store how many times we get nods from each player
        self.nods = {}
        # store how many times player shakes head
        self.shakes = {}
        self.current_gossip = 0

        self.consecutive_shakes = 0  # track consecutive shakes
        self.turn_number = 0  # track the turn number
        self.shake_pct = 0  # tracks the pct of shakes in the last listen
        self.latest_playerpositions = []

    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move

    def observe_before_turn(self, player_positions):
        self.latest_playerpositions = player_positions

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)

    def observe_after_turn(self, player_actions):
        pass

    def find_empty_seat(self):
        '''
        currently picking a seat randomly
        '''

        occupied_seats = set()

        # Collect the occupied seats
        for player_position in self.latest_playerpositions:
            table_num, seat_num = player_position[1], player_position[2]
            occupied_seats.add((table_num, seat_num))

        empty_seats = []

        # iterate through tables and seats to find empty seats
        for table_num in range(0, 10):
            for seat_num in range(0, 10):
                if (table_num, seat_num) not in occupied_seats:
                    empty_seats.append([table_num, seat_num])

        # so that it doesn't keep trying to go to the first few tables
        random.shuffle(empty_seats)

        return empty_seats

    def get_action(self):
        self.turn_number += 1

        # TODO: change so that it moves when shake pct is high
        move = random.randint(0, 2)
        # if self.shake_pct >= .88:
        if move == 1:
            self.shake_pct = 0  # Reset the shake count
            # Logic to move to a new seat
            priList = self.find_empty_seat()

            return 'move', priList

        # TODO: remove when current_gossip is set
        self.current_gossip = max(self.gossip_list)

        has_high_value_gossip = self.current_gossip > 70

        # If the player has high-value gossip, increase the chance of talking
        if has_high_value_gossip:
            action_type = random.choices(
                population=[0, 1],  # talk, listen
                weights=[0.7, 0.3],
                k=1
            )[0]
        else:
            # talk or listen will be random otherwise
            action_type = random.randint(0, 1)

        # On even turns, talk/listen to the left
        if self.turn_number % 2 == 0:
            if action_type == 0:
                return 'talk', 'left', self.current_gossip
            else:
                return 'listen', 'right'
        else:
            if action_type == 0:
                return 'talk', 'right', self.current_gossip
            else:
                return 'listen', 'left'

    def feedback(self, feedback):
        # store which players nods and shakes head and how many times
        if feedback != []:
            # nods head
            if feedback[0][0] == 'N':
                self.__nod_head(feedback)
            # shakes head
            else:
                self.__shake_head(feedback)

    def __nod_head(self, feedback):
        player = int(feedback[0][9:])
        if player in self.nods:
            self.nods[player] += 1
        else:
            self.nods[player] = 1

    def __shake_head(self, feedback):
        player = int(feedback[0][11:])
        if player in self.shakes:
            self.shakes[player] += 1
        else:
            self.shakes[player] = 1

    def get_gossip(self, gossip_item, gossip_talker):
        # store gossip item and talkers
        self.__add_gossip_item(gossip_item)
        self.__add_gossip_talker(gossip_talker)

    def __add_gossip_item(self, gossip_item):
        # count how many times we hear the same gossip
        if gossip_item in self.gossip_items:
            self.gossip_items[gossip_item] += 1
        else:
            self.gossip_items[gossip_item] = 1

    def __add_gossip_talker(self, gossip_talker):
        # count how many times we listen to same talker
        if gossip_talker in self.gossip_talkers:
            self.gossip_talkers[gossip_talker] += 1
        else:
            self.gossip_talkers[gossip_talker] = 1
