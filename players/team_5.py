from __future__ import annotations

import os
import random
import functools
import glob
import time

import numpy as np

import gymnasium
from gymnasium.spaces import Discrete

import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from pettingzoo.utils import parallel_to_aec

from RLEnvironment.wedding_gossip_env import wedding_gossip_environment_v1


CHECKPOINT_PATH="RLEnvironment/"
ENV_NAME="wedding_gossip_environment_v1"

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

        try:
            latest_policy = max(
                glob.glob(f"{CHECKPOINT_PATH}{ENV_NAME}*.zip"), key=os.path.getctime
            )
        except ValueError:
            print("Policy not found.")
            exit(0)

        # load the trained model
        self.model = PPO.load(latest_policy)


    # At the beginning of a turn, players should be told who is sitting where, so that they can use that info to decide if/where to move
    def observe_before_turn(self, player_positions):
        """
            player_positions - 3-dimensional tuple: (player_id, table_num, seat_num)
        """

        # print(f'Before:- id - {self.id}, team_num - {self.team_num}, table_num - {self.table_num}, seat_num - {self.seat_num}, gossip_list - {self.gossip_list} || player_positions - {player_positions}')

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
        # print(f'After:- id - {self.id}, team_num - {self.team_num}, table_num - {self.table_num}, seat_num - {self.seat_num}, gossip_list - {self.gossip_list} || player_actions - {player_actions}')

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

        observation = np.array(
            self.observations['seating'] +
            self.observations['gossip'] +
            self.observations['actions']
        )

        action, goss, pref = self.model.predict(observation)[0]

        if action < 2:
            return self.num_action_map[action][0], self.num_action_map[action][1]
        elif action < 4:
            goss = goss if self.observations['gossip'][goss-1] else max(self.gossip_list)
            return self.num_action_map[action][0], self.num_action_map[action][1], goss
        else:
            empty = self._get_empty()
            empty[0], empty[pref] = empty[pref], empty[0]
            return self.num_action_map[action], empty
        
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
