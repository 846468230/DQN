import gym
from simulations.single_episode import Episode
from main import machine_config, tasks
from gym import spaces
from gym.utils import seeding
from simulations.accelerator import CPU, GPU, FPGA, MLU
import numpy as np


class Single_virtual(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        episode = Episode(machine_config, tasks, None, None)
        self.machine = episode.simulation.machine
        self.action_space = spaces.Discrete(len(episode.simulation.machine.accelerators))
        high = np.array([1000 for i in range(10)])
        low = np.array([0 for i in range(10)])
        self.observation_space = spaces.Box(low, high)
        self._seed()
        self.t = 0

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        state = self.state
        self.t += 1
        done = self.t < 1000 #len(self.machine.task_instances)
        if not done:
            reward = 1
        else:
            reward = 0
        return self.observation_space.sample(), reward, done, {}

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self):
        episode = Episode(machine_config, tasks, None, None)
        self.machine = episode.simulation.machine
        self.state = np.array([
            self.machine.accelerators_original_power_consumption(CPU),
            0,
            self.machine.accelerators_original_power_consumption(GPU),
            0,
            self.machine.accelerators_original_power_consumption(MLU),
            0,
            self.machine.accelerators_original_power_consumption(FPGA),
            0,
            self.machine.power_total,
            self.machine.throughput_total,
        ])
        self.steps_beyond_done = None
        return np.array(self.state)

    def __call__(self, machine, clock):
        accelerators = machine.accelerators
        tasks = machine.tasks_which_has_waiting_instance
        candidate_task = None
        candidate_accelerator = None

        for accelerator in accelerators:
            for task in tasks:
                if accelerator.accommodate(task):
                    candidate_accelerator = accelerator
                    candidate_task = task
                    break
        return candidate_accelerator, candidate_task

    # get the throughput of different accelerator
    # def get_throughput(self):
    #     return self.get_cpu_throughput() + self.get_gpu_throughput() + self.get_mlu_throughput() + self.get_fpga_throughput()
    #
    # def get_cpu_throughput(self):
    #     return has_parameter(self, '_cpu_throughput')
    #
    # def get_gpu_throughput(self):
    #     return has_parameter(self, '_gpu_throughput')
    #
    # def get_mlu_throughput(self):
    #     return has_parameter(self, '_mlu_throughput')
    #
    # def get_fpga_throughput(self):
    #     return has_parameter(self, '_fpga_throughput')
    #
    # # get the power consumption of different accelerator
    # def get_PowerConsumption(self):
    #     return self.get_cpu_power_consumption() + self.get_gpu_power_consumption() + self.get_mlu_power_consumption() + self.get_fpga_power_consumption()
    #
    # def get_cpu_power_consumption(self):
    #     return has_parameter(self, '_cpu_powerConsumption')
    #
    # def get_gpu_power_consumption(self):
    #     return has_parameter(self, '_gpu_powerConsumption')
    #
    # def get_mlu_power_consumption(self):
    #     return has_parameter(self, '_mlu_powerConsumption')
    #
    # def get_fpga_power_consumption(self):
    #     return has_parameter(self, '_fpga_powerConsumption')
