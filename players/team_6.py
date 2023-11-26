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

    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move

    def observe_before_turn(self, player_positions):
        # TODO: does not seem to have any data?
        pass

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)

    def observe_after_turn(self, player_actions):
        pass

    def get_action(self):
        self.turn_number += 1

        # Check if the player has any high-value gossip
        # likelihood of choosing to talk is increased to 60% (compared to 20% for listening and 20% for moving)
        has_high_value_gossip = any(gossip > 70 for gossip in self.gossip_list)

        # If the player has high-value gossip, increase the chance of talking
        if has_high_value_gossip:
            action_type = random.choices(
                population=[0, 1, 2],
                weights=[0.6, 0.2, 0.2],
                k=1
            )[0]
        else:
            action_type = random.randint(0, 2)

        # talk
        if action_type == 0:
            direction = random.choice(['left', 'right'])
            gossip = random.choice(self.gossip_list)
            return 'talk', direction, gossip

        # listen
        elif action_type == 1:
            direction = random.choice(['left', 'right'])
            return 'listen', direction

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
