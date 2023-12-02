import os
import random
import functools
import numpy as np

import gymnasium
from gymnasium.spaces import Discrete

from ray.rllib.algorithms.ppo import PPO
from ray.rllib.algorithms.ppo import PPOConfig
from RLEnvironment.wedding_gossip_env.env.wedding_gossip_environment import WeddingGossipEnvironment
from ray.rllib.env.multi_agent_env import MultiAgentEnv, make_multi_agent # from - https://discuss.ray.io/t/bug-env-must-be-one-of-the-supported-types-baseenv-gym-env-multiagentenv-vectorenv-remotebaseenv/5704/2
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env
import ray

CHECKPOINT_PATH="RLEnvironment/~/results/version0/PPO/PPO_version0_f6458_00000_0_2023-12-01_20-41-50/params.json"

__all__ = ["WeddingGossipEnvironment"]

class Player():
    def __init__(self, id, team_num, table_num, seat_num, unique_gossip, color, turns):
        self.id = id
        self.team_num = team_num
        self.table_num = table_num
        self.seat_num = seat_num
        self.seat_id = self.table_num * 10 + seat_num # 0-99 format of seating

        self.color = color
        self.unique_gossip = unique_gossip
        self.gossip_list = [unique_gossip]
        self.group_score = 0
        self.individual_score = 0

        """
        # each tuple stores the following for seat 'seat_num' at table 'table_num'
        # 0 index - last observed action done by the player (initialized to None) - can be 'speak' or 'listen'
        # 1 index - direction of the action represented in action 0 (initialized to None) - can be 'left' or right
        # 2 index - player_id of last observed player at the seat (initialized to None)
        # 3 index - time_stamp of last observation (initialized to -1)
        self._curr_state = {seat_id: (None, None, None, -1) for seat_num in range(10)} for table_num in range(10)}

        # a hash mapping player_ids to where they are situated on the board
        # each player_id is mapped to (table_num, seat_num)
        # initialized to (None, None)
        self.player_seat_map = {p_id: (None, None) for p_id in range(90)}

        # action_to_num - to convert action into numerical value for model training purposes
        # can change the values to larger difference if this affects the model training
        self.action_to_num = {('speak', 'left'): 1,
                              ('speak', 'right'): 2,
                              ('listen', 'left'): 3,
                              ('listen', 'right'): 4}
        """

        # update it at every step! (currently updating it when the 'observe_after_turn' is called)
        self.time_stamp = 0
        
        # Most recent 4 observation spaces:
        # dimension - 90        x       90    x 90 (#players)
        #             100       x       2     x  5
        #             #seats    x gossip      x ll/lr/tl/tr/move
        self.observations = {'seating': [-1] * 90,
                             'gossip':  [False] * 90,
                             'actions': [4] * 90}
        
        # update our current position in observations!
        self.observations['seating'][self.id] = self.seat_id # where we are sitting
        self.observations['gossip'][unique_gossip - 1] = True # had to subtract one, because the gossips go from 1-90

        self.action_to_val_map = {'listen-left':    0,
                                  'listen-right':   1,
                                  'talk-left':      2,
                                  'talk-right':     3}
        
        # load the trained model
        self.ppo_model = self.load_trained_model()
        # PPO.from_checkpoint(CHECKPOINT_PATH)


    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        """
            player_positions - 3-dimensional tuple: (player_id, table_num, seat_num)
        """

        print(f'Before:- id - {self.id}, team_num - {self.team_num}, table_num - {self.table_num}, seat_num - {self.seat_num}, gossip_list - {self.gossip_list} || player_positions - {player_positions}')

        # update the observations['seating']
        for inst in player_positions:
            self.observations['seating'][inst[0]] = inst[1] * 10 + inst[2]
        
        # also update current seat_id, table_num, seat_num etc. 
        self.seat_id   = self.observations['seating'][self.id]
        self.table_num = self.observations['seating'][self.id] // 10
        self.seat_num  = self.observations['seating'][self.id] % 10


    # At the end of a turn, players should be told what everybody at their current table (who was there at the start of the turn)
    # did (i.e., talked/listened in what direction, or moved)
    def observe_after_turn(self, player_actions):
        """
            player_actions - 2-dimensional list: [player_id, [player_action[0], player_action[1]]]. Where player_action[0] can be 'talk' or 'listen', and player_action[1] can be 'left' or 'right'
        """

        # update the global timer
        self.time_stamp += 1
        print(f'After:- id - {self.id}, team_num - {self.team_num}, table_num - {self.table_num}, seat_num - {self.seat_num}, gossip_list - {self.gossip_list} || player_actions - {player_actions}')

        # update the observations['action']
        # reset everthing to 4 i.e. none first
        self.observations['actions'] = [4] * 90
        for inst in player_actions:
            self.observations['actions'][inst[0]] = self.action_to_val_map[inst[1][0] + '-' + inst[1][1]]
        
        # for seat_id in range(self.table_num * 10, self.table_num * 10 + 10):

    def get_action(self):
        # return 'talk', 'left', <gossip_number>
        # return 'talk', 'right', <gossip_number>
        # return 'listen', 'left', 
        # return 'listen', 'right', 
        # return 'move', priority_list: [[table number, seat number] ...]

        flattened_observation = self.observations['seating'].extend(self.observations['gossip']).extend(self.observations['actions'])

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
        print('Feedback:', feedback)

    def get_gossip(self, gossip_item, gossip_talker):
        print('Get gossip:', gossip_item, gossip_talker)

        # update the observation['gossip']
        self.observations['gossip'][gossip_item - 1] = True # had to subtract one, because the gossips go from 1-90
    
    def env_creator(self, args):
        env = WeddingGossipEnvironment()
        return env

    def load_trained_model(self):
        # return Algorithm.from_checkpoint(CHECKPOINT_PATH)
        # """
        env_name = "version0"

        ray.init()

        register_env(env_name, lambda config: PettingZooEnv(self.env_creator()))
        # return PPO.from_checkpoint(CHECKPOINT_PATH)

        config = (
            PPOConfig()
            .environment(env=env_name, clip_actions=True, disable_env_checking=True)
            .rollouts(num_rollout_workers=4, rollout_fragment_length=128)
            .training(
                train_batch_size=512,
                lr=2e-5,
                gamma=0.99,
                lambda_=0.9,
                use_gae=True,
                clip_param=0.4,
                grad_clip=None,
                entropy_coeff=0.1,
                vf_loss_coeff=0.25,
                sgd_minibatch_size=64,
                num_sgd_iter=10,
            )
            .debugging(log_level="ERROR")
            .framework(framework="torch")
            .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
        )

        # found this here - https://docs.ray.io/en/master/rllib/rllib-training.html#configuring-rllib-algorithms
        # Got here from long github discussion here - https://github.com/ray-project/ray/issues/4569
        algo = PPO(config=config, env=WeddingGossipEnvironment)
        return algo.restore(CHECKPOINT_PATH)
        # """

'''

############### Ignore from this point onwards - code parking lot

# implementation of the reward function goes here!
def reward_func(_states, _action, player_info):
    pass


# dicts to convert actions into human readable informaiton
DONT_KNOW = 5
POSSIBLE_ACTIONS = {1: 'speak-left',
                    2: 'speak-right',
                    3: 'listen-left',
                    4: 'listen-right',
                    5: "don't know",
                    6: 'move-1',
                    7: 'move-2',
                    8: 'move-3',
                    9: 'move-4',
                    10: 'move-5',
                    11: 'move-6',
                    12: 'move-7',
                    13: 'move-8',
                    14: 'move-9',
                    15: 'move-10'}

POSSIBLE_OBSERVATIONS = {1: 'speak-left',
                    2: 'speak-right',
                    3: 'listen-left',
                    4: 'listen-right',
                    5: "don't know"}

class game_env(AECEnv):
    """
    The metadata holds environment constants. From gymnasium, we inherit the "render_modes",
    metadata which specifies which modes can be put into the render() method.
    At least human mode should be supported.
    The "name" metadata allows the environment to be pretty printed.
    """

    metadata = {"render_modes": ["human"], "name": "wedding_gossip_v1"}

    def __init__(self, render_mode=None, termination_limit=100):
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

        # termination after this number of steps
        self.termination_limit = termination_limit

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
        self.state = {agent: DONT_KNOW for agent in self.agents}
        self.observations = {agent: DONT_KNOW for agent in self.agents}
        self.num_moves = 0

        # each tuple stores the following for seat 'seat_num' at table 'table_num'
        # 0 index - last observed action done by the player at seat_id (initialized to None) 
        #           can be 'speak-left', 'speak-right' 'listen-left', 'listen-'right' or 'don't know'
        #           check out POSSIBLE_OBSERVATIONS for exact mapping
        # 2 index - player_id of last observed player at the seat (initialized to None)
        # 3 index - time_stamp of last observation (initialized to -1)
        self._wedding_state = {seat_id: (DONT_KNOW, None, -1) for seat_id in range(100)}

        # a hash mapping player_ids to where they are situated on the board
        # each player_id is mapped to a number from 0-99. 
        # table_num = value % 10 (0-9)
        # seat_num = value / 10 (0-9)
        # initialized to None
        self.player_seat_map = {p_id: None for p_id in range(90)}

        """
        Our agent_selector utility allows easy cyclic stepping through the agents list.
        """
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

    def obtain_observations(self, _action, _player):
        """
            Use the class variables to obtain the observations given an action taken by the _player (i.e. agent).
        """
        pass

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
        - state
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

        # stores action of current agent
        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            # rewards for all agents are placed in the .rewards dictionary
            self.rewards = reward_func(self.player_seat_map, self._wedding_state)

            self.num_moves += 1
            # The truncations dictionary must be updated for all players.
            self.truncations = {
                agent: self.num_moves >= self.termination_limit for agent in self.agents
            }

            # observe the current state
            for i in self.agents:
                self.observations[i] = self.state[
                    self.agents[1 - self.agent_name_mapping[i]]
                ]
        else:
            # necessary so that observe() returns a reasonable observation at all times.
            self.state[self.agents[1 - self.agent_name_mapping[agent]]] = NONE
            # no rewards are allocated until both players give an action
            self._clear_rewards()

        if self.render_mode == "human":
            self.render()


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
'''