import simpy
from simulations.scheduler import Scheduler
from simulations.broker import Broker
from simulations.simulation import Simulation


class Episode(object):
    broker_cls = Broker

    def __init__(self, machine_configs, task_configs, algorithm, event_file):
        self.env = simpy.Environment()
        # self.env = simpy.rt.RealtimeEnvironment(factor=0.01, strict=False)
        machine = Machine(self.env, machine_configs)

        task_broker = Episode.broker_cls(self.env, task_configs)

        scheduler = Scheduler(self.env, algorithm)

        self.simulation = Simulation(self.env, machine, task_broker, scheduler, event_file)

    def run(self):
        self.simulation.run()
        self.env.run()


if __name__ == "__main__":
    from simulations.alogrithm import Algorithm
    from simulations.machine import Machine, MachineConfig
    from simulations.accelerator import CPUConfig,MLUConfig,FPGAConfig
    from simulations.task_generator import task_generator
    from simulations.config import task_types,accelerators,trace_base
    import os


    class FirstFitAlgorithm(Algorithm):
        def __call__(self, machine, clock):
            accelerators = machine.free_accelerators
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

    #
    accelerator_configs = []
    # for i in range(3):
    #     cpu_configs.append(CPUConfig(speed=1, frequency=2.3e9, cache=4e6, power_consumption=65, runtime=None))
    mlu = MLUConfig(1,28,31)
    fpga = FPGAConfig(1,46,43)
    accelerator_configs.append(mlu)
    accelerator_configs.append(fpga)
    machine_config = MachineConfig(accelerator_configs, 4000000000, 512000000000)
    tasks =  task_generator(os.path.join(trace_base, "_".join(task_types) + ".csv"),task_types,accelerators)
    episode = Episode(machine_config, tasks, FirstFitAlgorithm(), None)
    episode.run()
