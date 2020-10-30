from .alogrithm import Algorithm
from simulations.accelerator import CPU, GPU, FPGA, MLU
import numpy as np
from algorithms.rl_brain import DeepQNetwork


class DQNAlgorithm(Algorithm):
    name = "DQN"

    def __init__(self, RL):
        self.totel_steps = 0
        self.mode = "queqe"
        self.RL = RL
        self.ep_r = 0
        self.train = True

    def register_attributes(self,env,machine):
        self.env = env
        self.machine = machine
        self.ep_r = 0

    def generate_reward(self,not_complete_memory):
        yield self.env.timeout(10)
        #the length of the observation is 10
        state_ = []
        for accelerator in self.machine.accelerators:
            state_.append(accelerator.power_consumption)
            state_.append(accelerator.throughput)
        state_.append(self.machine.power_total)
        state_.append(self.machine.throughput_total)
        state_ = np.array(state_)
        reward = (-(self.machine.power_total - not_complete_memory[0][-2]) + self.machine.throughput_total - not_complete_memory[0][-1]) * 0.1
        self.ep_r += reward
        not_complete_memory.extend([reward,state_])
        self.RL.store_transition(*not_complete_memory)
        if self.totel_steps > 1000 and self.train:
            self.RL.learn()

    def __call__(self, machine, clock):
        accelerators = machine.free_accelerators
        if len(accelerators) == 0 :
            return None, None
        # tasks = machine.tasks_which_has_waiting_instance
        task = machine.head_task_instance
        if task is None:
            return None, None
        state = []
        for accelerator in machine.accelerators:
            state.append(accelerator.power_consumption)
            state.append(accelerator.throughput)
        state.append(machine.power_total)
        state.append(machine.throughput_total)
        state = np.array(state)
        action = self.RL.choose_action(state,self.train)
        not_complete_memory = [state,action]
        self.env.process(self.generate_reward(not_complete_memory))
        candidate_task = task
        candidate_accelerator = machine.accelerators[action]
        self.totel_steps += 1
        return candidate_accelerator, candidate_task
