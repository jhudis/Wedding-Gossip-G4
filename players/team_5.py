import random
import functools
import numpy as np

import gymnasium as gym
from gymnasium.spaces import Discrete

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers


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
                              ('speak', 'right'): 2,
                              ('listen', 'left'): 3,
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

############### Ignore from this point onwards - code parking lot


# implementation of the reward function goes here!
def reward_func(_states, _action, player_info):
    pass


# dicts to convert actions into human readable informaiton
POSSIBLE_ACTIONS = {1: 'speak-left',
                    2: 'speak-right',
                    3: 'listen-left',
                    4: 'listen-right',
                    5: 'move-1',
                    6: 'move-2',
                    7: 'move-3',
                    8: 'move-4',
                    9: 'move-5',
                    10: 'move-6',
                    11: 'move-7',
                    12: 'move-8',
                    13: 'move-9',
                    14: 'move-10'}

POSSIBLE_OBSERVATIONS = {1: 'speak left',
                    2: 'speak right',
                    3: 'listen left',
                    4: 'listen right',
                    5: "don't know"}

class game_env(AECEnv):
    """
    The metadata holds environment constants. From gymnasium, we inherit the "render_modes",
    metadata which specifies which modes can be put into the render() method.
    At least human mode should be supported.
    The "name" metadata allows the environment to be pretty printed.
    """

    metadata = {"render_modes": ["human"], "name": "wedding_gossip_v1"}

    def __init__(self, render_mode=None):
        """
        The init method takes in environment arguments and
         should define the following attributes:
        - possible_agents
        - render_mode

        Note: as of v1.18.1, the action_spaces and observation_spaces attributes are deprecated.
        Spaces should be defined in the action_space() and observation_space() methods.
        If these methods are not overridden, spaces will be inferred from self.observation_spaces/action_spaces, raising a warning.

        These attributes should not be changed after initialization.
        """

        # initialize agents for all 90 players. Can probably have just 10 for the table we are in
        self.possible_agents = ["player_" + str(r) for r in range(90)]

        # optional: a mapping between agent name and player_ID
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )

        # optional: we can define the observation and action spaces here as attributes to be used in their corresponding methods
        self._action_spaces = {agent: Discrete(len(POSSIBLE_ACTIONS)) for agent in self.possible_agents}


        # Since we can only observe 10 players, we'll need to mask the observations for other players. For that, I've created another bogous key 'nothing'
        self._observation_spaces = {
            agent: Discrete(len(POSSIBLE_OBSERVATIONS)) for agent in self.possible_agents
        }

        self.render_mode = render_mode

    # Observation space should be defined here.
    # lru_cache allows observation and action spaces to be memoized, reducing clock cycles required to get each agent's space.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
        return Discrete(len(POSSIBLE_OBSERVATIONS))
    
    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(len(POSSIBLE_ACTIONS))
    
    def render(self):
        """
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        """
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        if len(self.agents) == 90:
            string = "Current game state:\n"
            for player_id in range(90):
                string += f'player_{player_id}' + POSSIBLE_OBSERVATIONS[self.state[self.agents[player_id]]] + ' '
        else:
            string = "Game over"
        print(string)

    def observe(self, agent):
        """
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        """
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])
    
    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass
    
    def reset(self, seed=None, options=None):
        """
        Reset needs to initialize the following attributes
        - agents
        - rewards
        - _cumulative_rewards
        - terminations
        - truncations
        - infos
        - agent_selection
        And must set up the environment so that render(), step(), and observe()
        can be called without issues.
        Here it sets up the state dictionary which is used by step() and the observations dictionary which is used by step() and observe()
        """
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: NONE for agent in self.agents}
        self.observations = {agent: NONE for agent in self.agents}
        self.num_moves = 0
        """
        Our agent_selector utility allows easy cyclic stepping through the agents list.
        """
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

    def step(self, action):
        """
        step(action) takes in an action for the current agent (specified by
        agent_selection) and needs to update
        - rewards
        - _cumulative_rewards (accumulating the rewards)
        - terminations
        - truncations
        - infos
        - agent_selection (to the next agent)
        And any internal state used by observe() or render()
        """
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            # handles stepping an agent which is already dead
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next dead agent,  or if there are no more dead agents, to the next live agent
            self._was_dead_step(action)
            return

        agent = self.agent_selection

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[agent] = 0


# POSSIBLE_ACTIONS = {('speak', 'left'): 1,
#                     ('speak', 'right'): 2,
#                     ('listen', 'left'): 3,
#                     ('listen', 'right'): 4,
#                     ('move', '1'): 5,
#                     ('move', '2'): 6,
#                     ('move', '3'): 7,
#                     ('move', '4'): 8,
#                     ('move', '5'): 9,
#                     ('move', '6'): 10,
#                     ('move', '7'): 11,
#                     ('move', '8'): 12,
#                     ('move', '9'): 13,
#                     ('move', '10'): 14}

# POSSIBLE_OBSERVATIONS = {('speak', 'left'): 1,
#                     ('speak', 'right'): 2,
#                     ('listen', 'left'): 3,
#                     ('listen', 'right'): 4,
#                     ("don't know", "don't know"): 5,
#                     ('empty', 'empty'): 6}