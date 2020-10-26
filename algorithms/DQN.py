from .alogrithm import Algorithm
from simulations.accelerator import CPU, GPU, FPGA, MLU
import numpy as np
from rl_brain import DeepQNetwork


class DQNAlgorithm(Algorithm):
    name = "DQN"

    def __init__(self, RL):
        self.totel_steps = 0
        self.mode = "queqe"
        self.RL = RL
        self.ep_r = 0

    def register_attributes(self,env,machine):
        self.env = env
        self.machine = machine

    def generate_reward(self,not_complete_memory):
        yield self.env.timeout(4)
        #the length of the observation is 10
        state_ = np.array([
            self.machine.accelerators_original_power_consumption(CPU),
            self.machine.accelerators_throughput(CPU),
            self.machine.accelerators_original_power_consumption(GPU),
            self.machine.accelerators_throughput(GPU),
            self.machine.accelerators_original_power_consumption(MLU),
            self.machine.accelerators_throughput(MLU),
            self.machine.accelerators_original_power_consumption(FPGA),
            self.machine.accelerators_throughput(FPGA),
            self.machine.power_total,
            self.machine.throughput_total,
        ])
        reward = (-(self.machine.power_total - not_complete_memory[0][-2]) + self.machine.throughput_total - not_complete_memory[0][-1]) * 0.1
        self.ep_r += reward
        not_complete_memory.extend([reward,state_])
        self.RL.store_transition(*not_complete_memory)
        if self.totel_steps > 1000:
            self.RL.learn()

    def __call__(self, machine, clock):
        # accelerators = machine.free_accelerators
        tasks = machine.tasks_which_has_waiting_instance
        if not tasks:
            return None, None
        state = np.array([
            machine.accelerators_original_power_consumption(CPU),
            machine.accelerators_throughput(CPU),
            machine.accelerators_original_power_consumption(GPU),
            machine.accelerators_throughput(GPU),
            machine.accelerators_original_power_consumption(MLU),
            machine.accelerators_throughput(MLU),
            machine.accelerators_original_power_consumption(FPGA),
            machine.accelerators_throughput(FPGA),
            machine.power_total,
            machine.throughput_total,
        ])
        task = machine.head_task_instance
        action = self.RL.choose_action(state)
        not_complete_memory = [state,action]
        self.env.process(self.generate_reward(not_complete_memory))
        candidate_task = task
        candidate_accelerator = machine.accelerators[action]
        self.totel_steps += 1
        return candidate_accelerator, candidate_task
