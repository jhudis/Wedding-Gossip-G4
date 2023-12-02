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
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.tune.registry import register_env
import ray
from ray import tune

CHECKPOINT_PATH="RLEnvironment/~/results/version0/PPO/PPO_version0_f2865_00000_0_2023-12-02_13-38-12/checkpoint_000000"

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
 
        self.num_action_map = {
                0: ('listen', 'left'),
                1: ('listen', 'right'),
                2: ('talk', 'left'),
                3: ('talk', 'right'),
                4: ('move')
        }       

        # load the trained model
        # self.ppo_model = self.load_trained_model()
        self.agent = PPO.from_checkpoint(CHECKPOINT_PATH)


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

        observation = np.array([
            self.observations['seating'],
            self.observations['gossip'],
            self.observations['actions']
        ])

        action, goss, pref = self.agent.compute_single_action(observation)

        if action < 2:
            return self.num_action_map[action]
        elif action < 4:
            goss = goss if self.observations['gossip'][goss-1] else max(self.gossip_list)
            return self.num_action_map[action], goss
        else:
            empty = self._get_empty()
            empty[0], empty[pref] = empty[pref], empty[0]
            return self.num_action_map[action], pref
        
    def _get_empty(self):
        ret = []
        for seat in range(100):
            if seat not in self.observations['seating']:
                ret.append([seat//10, seat%10])

        return ret

    def feedback(self, feedback):
        # print('Feedback:', feedback)
        pass

    def get_gossip(self, gossip_item, gossip_talker):
        # print('Get gossip:', gossip_item, gossip_talker)
        self.gossip_list.append(gossip_item)

        # update the observation['gossip']
        self.observations['gossip'][gossip_item - 1] = True # had to subtract one, because the gossips go from 1-90

    def env_creator(self, args):
        env = WeddingGossipEnvironment()
        return env

    def load_trained_model(self):
        # return Algorithm.from_checkpoint(CHECKPOINT_PATH)
        # """
        env_name = "version0"

        register_env(env_name, lambda config: PettingZooEnv(self.env_creator(config)))
        # # return PPO.from_checkpoint(CHECKPOINT_PATH)

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

        return PPO.from_checkpoint(CHECKPOINT_PATH)

        # found this here - https://docs.ray.io/en/master/rllib/rllib-training.html#configuring-rllib-algorithms
        # Got here from long github discussion here - https://github.com/ray-project/ray/issues/4569
        # algo = PPO(config=config, env=WeddingGossipEnvironment)
        # return algo.restore(CHECKPOINT_PATH)
        # """
