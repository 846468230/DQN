import os
from algorithms.first_fit import FirstFitAlgorithm
from algorithms.random import RandomAlgorithm
from algorithms.DQN import DQNAlgorithm
from algorithms.heft import HeftAlgorithm
from simulations.machine import Machine, MachineConfig
from simulations.accelerator import CPUConfig,MLUConfig,FPGAConfig,GPUConfig
from simulations.task_generator import task_generator
from simulations.config import task_types,accelerators,trace_base,model_path,task_nums
from simulations.single_episode import Episode
from algorithms.rl_brain import DeepQNetwork

accelerator_configs = []
mlu = MLUConfig(1,28,31)
fpga = FPGAConfig(1,46,43)
gpu = GPUConfig()
accelerator_configs.append(mlu)
accelerator_configs.append(fpga)
accelerator_configs.append(gpu)
mlu = MLUConfig(1, 28, 31)
fpga = FPGAConfig(1, 46, 43)
cpu = CPUConfig()
gpu = GPUConfig()
accelerator_configs.append(mlu)
accelerator_configs.append(fpga)
accelerator_configs.append(gpu)
accelerator_configs.append(cpu)
machine_config = MachineConfig(accelerator_configs,4046,44712840,220)
tasks =  task_generator(os.path.join(trace_base, "_".join(task_types)+"_"+str(task_nums) + ".csv"),task_types,accelerators)
# episode = Episode(machine_config, tasks, RandomAlgorithm(), None)
# episode = Episode(machine_config, tasks, FirstFitAlgorithm(), None)
# episode = Episode(machine_config, tasks,HeftAlgorithm(), None)
# episode.run()
RL = DeepQNetwork(n_actions=len(accelerator_configs),
                  n_features=10,
                  learning_rate=0.01, e_greedy=0.9,
                  replace_target_iter=100, memory_size=2000,
                  e_greedy_increment=0.001, )



if __name__ == "__main__":
    # episode.run()
    from simulations.config import output_logs
    output_logs = False
    dqn_algorithms = DQNAlgorithm(RL)
    for i_episode in range(30):
        episode = Episode(machine_config, tasks, dqn_algorithms, None)
        dqn_algorithms.register_attributes(episode.env,episode.simulation.machine)
        episode.run()
        print('episode: ', i_episode, 'ep_r: ', round(dqn_algorithms.ep_r, 2), ' epsilon: ', round(RL.epsilon, 2))
    RL.plot_cost()
    RL.save_model(model_path)
    # RL.load_model("C:\\Users\\dao\\PycharmProjects\\DQN\\model_logs\\2020-10-27-19-08-06")
    # dqn_algorithms = DQNAlgorithm(RL)
    # dqn_algorithms.train = False
    # episode = Episode(machine_config, tasks, dqn_algorithms, None)
    # dqn_algorithms.register_attributes(episode.env, episode.simulation.machine)
    # episode.run()

