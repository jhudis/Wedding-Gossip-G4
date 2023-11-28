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

    def __init__(self, render_mode=None):
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
        return MultiDiscrete(np.array([5, 90, 90]))
