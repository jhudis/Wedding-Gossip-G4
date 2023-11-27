import random

class Player():
    def __init__(self, id, team_num, table_num, seat_num, unique_gossip, color):
        self.id = id
        self.team_num = team_num
        self.table_num = table_num
        self.seat_num = seat_num
        self.color = color
        self.unique_gossip = unique_gossip
        self.gossip_list = [Gossip(unique_gossip)]
        self.current_gossip = Gossip(unique_gossip)
        self.group_score = 0
        self.individual_score = 0

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

        self.current_gossip = self.get_new_gossip()

        has_high_value_gossip = self.current_gossip.get_item() > 70

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
                return 'talk', 'left', self.current_gossip.get_item()
            else:
                return 'listen', 'right'
        else:
            if action_type == 0:
                return 'talk', 'right', self.current_gossip.get_item()
            else:
                return 'listen', 'left'
            
    def get_max_gossip(self):
        max_gossip = self.current_gossip
        for gossip in self.gossip_list:
            if gossip.get_item() > max_gossip.get_item():
                max_gossip = gossip
        return gossip

    def feedback(self, feedback):
        # log each feedback for current gossip 
        for response in feedback:
            # nod
            if response[0] == 'N':
                self.current_gossip.add_nod(int(response[9:]), self.turn_number)
            # shake
            else:
                self.current_gossip.add_shake(int(response[11:]), self.turn_number)

    def get_gossip(self, gossip_item, gossip_talker):
        gossip = self.__get_gossip(gossip_item)
        # log new gossip!
        if gossip == None:
            gossip = Gossip(gossip_item)
            gossip.add_heard(gossip_talker, self.turn_number)
            self.gossip_list.append(gossip)
            self.gossip_list.sort(key=lambda x: x.get_item(), reverse=True)
        # alter existing gossip
        else:
            gossip.add_heard(gossip_talker, self.turn_number)

    def __get_gossip(self, gossip_item):
        for gossip in self.gossip_list:
            if gossip.get_item() == gossip_item:
                return gossip

    def get_new_gossip(self):
        for gossip in self.gossip_list:
            if len(gossip.shakes) < 45:
                return gossip
        return gossip[0]

# everytime we hear gossip we store talker, item and turn we received it
# can also use this to keep track of feedback we receive for particular gossip
class Gossip():
    def __init__(self, gossip_item: int):
        self.gossip_item = gossip_item
        # which players nod their head and on what turn
        self.nods = []
        # which players shake their head and on what turn
        self.shakes = []
        # which players told us this gossip on what turn
        self.heard = []

    def get_item(self):
        return self.gossip_item

    def add_nod(self, player: int, turn: int):
        self.nods.append([player, turn])
    
    def add_shake(self, player: int, turn: int):
        self.shakes.append([player, turn])

    def add_heard(self, player: int, turn: int):
        self.heard.append([player, turn])
        
    
