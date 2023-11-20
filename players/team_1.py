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

        # player to knowledge map
        self.player_gossip_map = {}
        self.turn_counter = 0


    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        pass

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):
        pass

    def get_action(self):
        self.turn_counter += 1
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]

        # move with 15% probability (this was just an arbitrary choice)
        # if gossip > 60, talk w/ 60% probability (this was just an arbitrary choice); else 25% (reverse for listen)
        talk_probability = 60
        if all(x < 60 for x in self.gossip_list):
            talk_probability = 25
        action_type = random.randint(0, 100)

        # talk
        if action_type < talk_probability:
            direction = self.turn_counter % 2
            gossip = random.choice(self.gossip_list)
            # talk left on even turns
            if direction == 0:
                return 'talk', 'left', gossip
            # right
            else:
                return 'talk', 'right', gossip
        
        # listen
        elif action_type < 85:
            direction = self.turn_counter % 2
            # listen left on odd turns
            if direction == 1:
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

    # add learned gossip to our gossip list and to the gossip list of the player we received it from... to be used later
    def get_gossip(self, gossip_item, gossip_talker):
        self.gossip_list.append(gossip_item)
        if gossip_talker not in self.player_gossip_map:
            self.player_gossip_map[gossip_talker] = [gossip_item]
        else:
            self.player_gossip_map[gossip_talker].append(gossip_item)
        pass