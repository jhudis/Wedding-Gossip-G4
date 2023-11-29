import random
import functools
from copy import copy
import numpy as np

from gymnasium.spaces import MultiDiscrete

from pettingzoo import ParallelEnv
from pettingzoo.utils import agent_selector, wrappers

# Action Constants
TALK_L = 0
TALK_R = 1
LISTEN_L = 2
LISTEN_R = 3
MOVE = 5
# Observation Constants (0-3 same as action)
NONE = 5

# Reward Params
ALPHA = 1
BETA = 1
GAMMA = 1
DELTA = 1

class WeddingGossipEnvironment(ParallelEnv):
    metadata = {"render_modes": ["human"], 
                "name": "wedding_gossip_environment_v0"}

    def __init__(self, player_seat_map, initial_gossips, render_mode=None):
        # player_seat_map - a dict of format {"player_id": seat_id} | seat_id -> 0-99
        # initial_gossips - a dict of format {"player_id": gossip_num}
        self.pos = None
        self.actions = None
        self.state = None

        self.possible_agents = ["player_" + str(r) for r in range(90)]

        # optional: a mapping between agent name and player_ID
        self.agent_name_mapping = dict(
            zip(self.possible_agents, 
                list(range(len(self.possible_agents)))
            )
        )
        self._agent_selector = agent_selector(self.agents)
        self.render_mode = render_mode


        # project specific variables - 
        # HAVE TO ADD THESE TO THE RESET FUNCTION AS WELL!

        # a hash mapping player_ids to where they are situated on the board
        # each player_id is mapped to a number from 0-99. 
        # table_num = value % 10 (0-9)
        # seat_num = value / 10 (0-9)
        # initialized to None
        self.player_seat_map = player_seat_map # {p_id: None for p_id in range(90)}
        
        # update the self.seating list - 100 size list based on player_seat_map
        self.update_seating()

        self.available_seats = self.get_available_seats()

        self.agent_gossips = initial_gossips # {agent: [] for agent in self.possible_agents}


    def reset(self, seed=None, options=None):
        """
        Reset needs to initialize the `agents` attribute and must set up the
        environment so that render(), and step() can be called without issues.
        Here it initializes the `num_moves` variable which counts the number of
        hands that are played.
        Returns the observations for each agent
        """
        self.agents = copy(self.possible_agents)
        self.timestep = 0
        self.pos = random.sample(range(100), k=90)
        self.actions = [5 * 90]

        init_obs = np.array(self.pos, [0 * 90], [5 * 10], [0 * 3])
        observations = {a: init_obs for a in self.agents}
        gossip = random.shuffle(range(90))
        for i, a in enumerate(observations.keys()):
            observations[a][1][gossip[i]] = 1

        # Get dummy infos. Necessary for proper parallel_to_aec conversion
        infos = {a: {} for a in self.agents}

        self.state = observations

        return observations, infos

    def step(self, actions):
        """
        step(action) takes in an action for each agent and should return the
        - observations
        - rewards
        - terminations
        - truncations
        - infos
        dicts where each dict looks like {agent_1: item_1, agent_2: item_2}
        """
        # If a user passes in actions with no agents, then just return empty observations, etc.
        if not actions:
            self.agents = []
            return {}, {}, {}, {}, {}

        # update the self.player_seat_map, and self.available_seats
        self.actions = actions   
        for agent in self.agents:
            # get action - a 5x90x10x10 array
            curr_action = self.actions[agent] # cross check that this is the way to obtain the action!
            
            # talk left
            if curr_action[0] == 0:
                chosen_gossip = curr_action[1]
                # check if gossip to share is present in the player's gossip list
                if chosen_gossip not in self.agent_gossips[agent]:
                    # return a highly negative reward!
                    pass
                else:
                    # check for confirmation! If the said gossip was well-received, then give positive reward!
                    pass
            # talk right
            elif curr_action[0] == 1:
                chosen_gossip = curr_action[1]
                # check if gossip to share is present in the player's gossip list
                if chosen_gossip not in self.agent_gossips[agent]:
                    # return a highly negative reward!
                    pass
                else:
                    # check for confirmation! If the said gossip was well-received, then give positive reward!
                    pass
            # listen left
            elif curr_action[0] == 2:
                # check if any of the left neighbors are speaking to their right!
                left_neighbors = self.get_left_neighbors(self.player_seat_map[agent])
                possible_gossips = []
                for neighbor in left_neighbors:
                    if self.actions[neighbor][0] == 0 or self.actions[neighbor][0] == 1:
                        possible_gossips.append(self.actions[neighbor])
                heard_gossip = max(possible_gossips) if len(possible_gossips) > 0 else -1
                # use this to return reward!
            # listen right
            elif curr_action[0] == 3:
                # check if any of the left neighbors are speaking to their right!
                right_neighbors = self.get_right_neighbors(self.player_seat_map[agent])
                possible_gossips = []
                for neighbor in right_neighbors:
                    if self.actions[neighbor][0] == 0 or self.actions[neighbor][0] == 1:
                        possible_gossips.append(self.actions[neighbor])
                heard_gossip = max(possible_gossips) if len(possible_gossips) > 0 else -1
                # use this to return reward!
                
            # move
            elif curr_action[0] == 4:
                move_choice_order = []
                move_choice_order.append(curr_action[2])
                move_choice_order.append(curr_action[3])
                # fill out the rest - 
                for i in np.random.shuffle(list(range(9))):
                    if i not in move_choice_order:
                        move_choice_order.append(i)
                pass
            else:
                # not possible, but if it does happen, give huge negative reward maybe?
                pass


        # rewards for all agents are placed in the rewards dictionary to be returned
        rewards = {}
        for a in actions: 
            """ reward function
            listen gossip i: + i * ALPHA
            talk gossip i: + i * num_nods - num_shake * BETA
            move: +GAMMA if success else -DELTA
            end: 1000000 / timestep (everyone has all gossip)
            """

        # Check termination conditions
        terminations = {agent: False for agent in self.agents}

        # Check truncation conditions (overwrites termination conditions)
        truncations = {a: False for a in self.agents}

        # Exit condition
        if any(terminations.values()) or all(truncations.values()):
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def render(self):
        print(self.state)
    
    def close(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return MultiDiscrete(np.array([100 * 90], [2 * 90], [5 * 10], [2 * 3]))

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return MultiDiscrete(np.array([5, 90, 10, 10]))
    
    def get_available_seats(self):
        """
            A function that looks at self.player_seat_map, and returns a tuple of size 10 containing the available seats.
        """
        return set(range(100)).difference(set(self.player_seat_map.values()))
    
    def update_seat_player_map(self):
        # a function to create and update the self.seating list - 100 size list. None represents empty seat!
        self.seating = [None] * 100
        for player_id in self.player_seat_map.keys():
            curr_seat = self.player_seat_map[player_id]
            self.seating[curr_seat] = player_id
        

    def get_left_neighbors(self, seat_id, _count=3):
        if _count > 9:
            print("CANT HAVE MORE THAN 9 LEFT NEIGHBORS!")
        
        neighbor_ids = []
        corner_seat = (seat_id // 10) * 10 # 0, 10, 20...
        for i in range(1, _count+1):
            curr_seat_id = seat_id - i if (seat_id - i) >= corner_seat else seat_id + (10 - i)
            neighbor_ids.append(self.seating[curr_seat_id])
        return neighbor_ids

    def get_right_neighbors(self, seat_id, _count=3):
        if _count > 9:
            print("CANT HAVE MORE THAN 9 RIGHT NEIGHBORS!")
        
        neighbor_ids = []
        corner_seat = ((seat_id // 10) + 1) * 10 - 1 # 9, 19, 29...
        for i in range(1, _count+1):
            curr_seat_id = seat_id + i if (seat_id + i) <= corner_seat else seat_id - (10 - i)
            neighbor_ids.append(self.seating[curr_seat_id])
        return neighbor_ids