import os

import ray
import supersuit as ss
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
# from ray.rllib.models import ModelCatalog
# from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.tune.registry import register_env
# from torch import nn

from pettingzoo.butterfly import pistonball_v6

from wedding_gossip_env import wedding_gossip_environment_v0
from wedding_gossip_env.env.wedding_gossip_environment import WeddingGossipEnvironment

def env_creator(args):
    env = WeddingGossipEnvironment()
    env = ss.flatten_v0(env)
    env = ss.frame_stack_v1(env, 4)
    return env


if __name__ == "__main__":
    ray.init()

    env_name = "version0"

    register_env(env_name, lambda config: ParallelPettingZooEnv(env_creator(config)))
    # ModelCatalog.register_custom_model("CNNModelV2", CNNModelV2)

    config = (
        PPOConfig()
        .environment(env=env_name, clip_actions=True)
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

    tune.run(
        "PPO",
        name="PPO",
        stop={"timesteps_total": 2028},
        checkpoint_freq=10,
        local_dir="~/results/" + env_name,
        config=config.to_dict(),
    )