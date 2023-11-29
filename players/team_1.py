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

        # player to knowledge map
        self.player_gossip_map = {}
        for i in range(90):
            self.player_gossip_map[i] = []

        self.turn_counter = 0

        # open seats
        self.open_seats = []

        # game map - (table number, seat number) = player number #-> -1 inserted in place of empty seat
        self.seating_arrangement = {}
        self.recent_gossip_shared = 0

        # record the actions each player is taking at your table
        self.action_counts = {}
        # record the action each player took -- ONLY FOR CURRENT TABLE
        self.previous_action = {}

        self.talk_actions = ['left', 'right']
        self.listen_actions = ['right', 'left']


    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    # list of thruples: player number, table num, seat num
    def observe_before_turn(self, player_positions):
        # populate seating arrangement
        for position in player_positions:
            self.seating_arrangement[(position[1], position[2])] = position[0]

        # update seat_num, table_num
        self.table_num = player_positions[self.id][1]
        self.seat_num = player_positions[self.id][2]

        # find empty seats
        for i in range(10):
            for j in range(10):
                if (i, j) not in self.seating_arrangement.keys():
                    self.seating_arrangement[(i, j)] = -1
                    self.open_seats.append((i, j))

    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):

        # I think action counts should count the past 3 turns and then be reset

        # we DECREMENT the counter -- so if we see a player's action, we decrement the count

        for player_action in player_actions:
            player, action = player_action

            print("player", player, "action", action)

            self.previous_action[player] = action

            act, direction = action

            # dict of dicts
            if player not in self.action_counts:

                count_dict = {"talk": {"right": 2, "left": 2}, "listen": {"right": 2, "left": 2}}

                count_dict[act][direction] -= 1

                self.action_counts[player] = count_dict

            else:
                self.action_counts[player][act][direction] -= 1
        # print("ACTION COUNTS", self.action_counts)
        pass

    def __check_actions_all_zeroes(self):
        for player, actions in self.action_counts.items():
            for action, directions in actions.items():
                for direction, count in directions.items():
                    if count != 0:
                        return False
        return True

    def __move_to_empty_seat(self):
        # move
        print("Moving")

        # find closest player with the best gossip in their knowledge base
        # if no such player exists, move to a random open seat

        # sort open seats by how crowded they are 3 seats in each direction
        seat_count = {}
        for seat in self.open_seats:
            seat_count[seat] = 0
            for i in range(1, 4):
                target_player = self.seating_arrangement[(seat[0], (seat[1] - i) % 10)]
                if target_player != -1:
                    seat_count[seat] += 1
                target_player = self.seating_arrangement[(seat[0], (seat[1] + i) % 10)]
                if target_player != -1:
                    seat_count[seat] += 1

        sorted_seats = sorted(seat_count.items(), key=lambda x: x[1], reverse=True)

        waitlist = []
        for seat in sorted_seats:
            if seat[0][0] != self.table_num:  # move to a different table
                waitlist.append([seat[0][0], seat[0][1]])

        return 'move', waitlist

    def get_action(self):
        self.turn_counter += 1
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]

        direction = self.turn_counter % 2

        if self.turn_counter == 1:
            # talk if gossip > 60

            # if all(x < 60 for x in self.gossip_list):
            # we need to coordinate this with the get gossip to share fxn

            # at this point, they should only have 1 piece of gossip
            if any(x > 60 for x in self.gossip_list):

                # print("here, gossip >= 60", self.gossip_list)

                gossip = self.get_gossip_to_share(direction)

                # print("gossip", gossip)

                # talk left on even turns
                if gossip:
                    self.recent_gossip_shared = gossip
                    return 'talk', self.talk_actions[direction], gossip
                return 'listen', self.listen_actions[direction]

            else:
                # print("here, gossip < 60", self.gossip_list)

                return 'listen', self.listen_actions[direction]

        else:
            # need to check the prev actions of the 3 players both to the left and right of me

            # Calculate the range for the seats to the left and right
            left_seats = [(self.seat_num - i) % 10 for i in range(1, 4)]
            right_seats = [(self.seat_num + i) % 10 for i in range(1, 4)]

            # need to map player versus seat versus action!

            players_by_seat = {}
            for table,seat in self.seating_arrangement.keys():
                player = self.seating_arrangement[(table, seat)]
                print("seating arr player", player)

                # -1 = empty seat at that table
                if player != -1:
                    if table == self.table_num:
                        # print("player", player)
                        # print("self.previous_action[player]", self.previous_action[player])
                        if player in self.previous_action.keys():
                            players_by_seat[seat] = {"id": player, "action": self.previous_action[player]}
                        else:
                            players_by_seat[seat] = {"id": player, "action": ("move", None)}

            # print("players", players_by_seat)

            # LOOKIN TALKIN LOGIC -- will make more elegant later

            # process people to the right
            my_prev_action, my_prev_direction = self.previous_action[self.id]

            if my_prev_action == "talk" and my_prev_direction == "left":
                # look at opposite side
                listen_count = 0
                talk_count = 0
                # move_count = 0

                for seat in right_seats:
                    if seat in players_by_seat.keys():
                        their_prev_action, their_prev_direction = players_by_seat[seat]["action"]

                        if their_prev_action == "talk":
                            talk_count += 1
                        elif their_prev_action == "listen":
                            listen_count += 1
                        # else:
                        #     move_count += 1


                # update our dicts based on the actions we saw
                if listen_count == 3:
                    self.action_counts[self.id]["talk"]["left"] = 0
                else:
                    self.action_counts[self.id]["talk"]["left"] -= 1


                # MOVE
                # now check if we should move based on if all actions in self.action_counts go to 0
                if self.__check_actions_all_zeroes():
                    # reset the actions counts to 2
                    self.action_counts = {"talk": {"right": 2, "left": 2}, "listen": {"right": 2, "left": 2}}

                    return self.__move_to_empty_seat()


                # check the OTHER side because we will have to talk to the RIGHT next turn for this condition
                if listen_count > 1 and self.action_counts[self.id]["talk"]["right"] > 0:
                    return 'talk', self.talk_actions[direction], self.recent_gossip_shared
                elif talk_count > 1:
                    return 'listen', self.listen_actions[(direction + 1) % 2]

            elif my_prev_action == "talk" and my_prev_direction == "right":
                # look at opposite side
                listen_count = 0
                talk_count = 0

                for seat in left_seats:
                    if seat in players_by_seat.keys():
                        their_prev_action, their_prev_direction = players_by_seat[seat]["action"]

                        if their_prev_action == "talk":
                            talk_count += 1
                        elif their_prev_action == "listen":
                            listen_count += 1
                        # else:
                        #     move_count += 1



                # update our dicts based on the actions we saw
                if listen_count == 3:
                    self.action_counts[self.id]["talk"]["right"] = 0
                else:
                    self.action_counts[self.id]["talk"]["right"] -= 1

                # MOVE
                # now check if we should move based on if all actions in self.action_counts go to 0
                if self.__check_actions_all_zeroes():
                    # reset the actions counts to 2
                    self.action_counts = {"talk": {"right": 2, "left": 2}, "listen": {"right": 2, "left": 2}}

                    return self.__move_to_empty_seat()

                # check the OTHER side because we will have to talk to the LEFT next turn for this condition
                if listen_count > 1 and self.action_counts[self.id]["talk"]["left"] > 0:
                    return 'talk', self.talk_actions[direction], self.recent_gossip_shared
                elif talk_count > 1:
                    return 'listen', self.listen_actions[(direction + 1) % 2]


            elif my_prev_action == "listen" and my_prev_direction == "left":
                # look at SAME side
                listen_count = 0
                talk_count = 0

                for seat in left_seats:
                    if seat in players_by_seat.keys():
                        their_prev_action, their_prev_direction = players_by_seat[seat]["action"]

                        if their_prev_action == "talk":
                            talk_count += 1
                        elif their_prev_action == "listen":
                            listen_count += 1
                        # else:
                        #     move_count += 1

                # update our dicts based on the actions we saw
                if listen_count == 3:
                    self.action_counts[self.id]["listen"]["left"] = 0
                else:
                    self.action_counts[self.id]["listen"]["left"] -= 1

                # MOVE
                # now check if we should move based on if all actions in self.action_counts go to 0
                if self.__check_actions_all_zeroes():
                    # reset the actions counts to 2
                    self.action_counts = {"talk": {"right": 2, "left": 2}, "listen": {"right": 2, "left": 2}}

                    return self.__move_to_empty_seat()

                # check the OTHER side because we will have to talk to the LEFT next turn for this condition
                if listen_count > 1 and self.action_counts[self.id]["talk"]["left"] > 0:
                    return 'talk', self.talk_actions[direction], self.recent_gossip_shared
                elif talk_count > 1:
                    return 'listen', self.listen_actions[(direction + 1) % 2]


            elif my_prev_action == "listen" and my_prev_direction == "right":
                # look at SAME side
                listen_count = 0
                talk_count = 0

                for seat in right_seats:
                    if seat in players_by_seat.keys():
                        their_prev_action, their_prev_direction = players_by_seat[seat]["action"]

                        if their_prev_action == "talk":
                            talk_count += 1
                        elif their_prev_action == "listen":
                            listen_count += 1
                        # else:
                        #     move_count += 1

                # update our dicts based on the actions we saw
                if listen_count == 3:
                    self.action_counts[self.id]["listen"]["right"] = 0
                else:
                    self.action_counts[self.id]["listen"]["right"] -= 1

                # MOVE
                # now check if we should move based on if all actions in self.action_counts go to 0
                if self.__check_actions_all_zeroes():
                    # reset the actions counts to 2
                    self.action_counts = {"talk": {"right": 2, "left": 2}, "listen": {"right": 2, "left": 2}}

                    return self.__move_to_empty_seat()

                # check the OTHER side because we will have to talk to the LEFT next turn for this condition
                if listen_count > 1 and self.action_counts[self.id]["talk"]["right"] > 0:
                    return 'talk', self.talk_actions[direction], self.recent_gossip_shared
                elif talk_count > 1:
                    return 'listen', self.listen_actions[(direction + 1) % 2]








    # add shared feedback to those player's knowledge base that received it 'Nod Head 12'
    def feedback(self, feedback):
        # feedback of form String + String + player number
        for feed in feedback:
            result = feed.split(' ')
            if result[0] == "Nod" or result[0] == "Shake":
                self.player_gossip_map[int(result[2])].append(self.recent_gossip_shared)

    # add learned gossip to our gossip list and to the gossip list of the player we received it from... to be used later
    def get_gossip(self, gossip_item, gossip_talker):
        self.gossip_list.append(gossip_item)
        self.player_gossip_map[gossip_talker].append(gossip_item)

    # share gossip value within a range determined by turn count
    # check to see if gossip is in target player's knowledge base
    # if gossip is not known by at least 2 players, talk, else listen
    def get_gossip_to_share(self, direction):
        # TODO: play around with value 30- currently every 30 turns, decrease range by 10 (i.e go from 70%-100% to 60%-90%)
        ceiling = (1 - ((self.turn_counter // 30) * .1)) * 90  # start at 100% of 90, then drops to 90% of 90, etc. for top of range
        floor = ceiling - 27  # 30% of 90 is 27
        gossip_in_range = [x for x in self.gossip_list if ceiling >= x >= floor]
        gossip_in_range.sort(reverse=True)
        neigh_dir = 1 if direction == 0 else -1
        for gos in gossip_in_range:
            known_count = 0
            for i in range(1, 4):
                target_player = self.seating_arrangement[(self.table_num, (self.seat_num - (neigh_dir * i)) % 10)]
                if target_player != -1:
                    if gos in self.player_gossip_map[target_player]:
                        known_count += 1
            if known_count < 2:
                return gos
        return None
