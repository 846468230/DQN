import os
from algorithms.first_fit import FirstFitAlgorithm
from algorithms.random import RandomAlgorithm
from simulations.machine import Machine, MachineConfig
from simulations.accelerator import CPUConfig,MLUConfig,FPGAConfig,GPUConfig
from simulations.task_generator import task_generator
from simulations.config import task_types,accelerators,trace_base
from simulations.single_episode import Episode



if __name__ == "__main__":

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
    tasks =  task_generator(os.path.join(trace_base, "_".join(task_types) + ".csv"),task_types,accelerators)
    # episode = Episode(machine_config, tasks, FirstFitAlgorithm(), None)
    # episode.run()
    episode = Episode(machine_config, tasks, RandomAlgorithm(), None)
    episode.run()