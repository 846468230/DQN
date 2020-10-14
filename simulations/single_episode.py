import simpy
from simulations.scheduler import Scheduler
from simulations.broker import Broker
from simulations.simulation import Simulation

class Episode(object):
    broker_cls = Broker

    def __init__(self, machine_configs, task_configs, algorithm, event_file):
        self.env = simpy.Environment()  # simpy.rt.RealtimeEnvironment(factor=0.01, strict=False)
        machine = Machine(self.env, machine_configs)

        task_broker = Episode.broker_cls(self.env, task_configs)

        scheduler = Scheduler(self.env, algorithm)

        self.simulation = Simulation(self.env, machine, task_broker, scheduler, event_file)

    def run(self):
        self.simulation.run()
        self.env.run()


if __name__ == "__main__":
    from simulations.alogrithm import Algorithm
    from simulations.config import TaskConfig
    from simulations.machine import Machine, MachineConfig
    from simulations.Accelerator import CPUConfig
    from random import randint


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


    cpu_configs = []
    for i in range(3):
        cpu_configs.append(CPUConfig(speed=1, frequency=2.3e9, cache=4e6, power_consumption=65, runtime=None))

    machine_config = MachineConfig(cpu_configs, 4000000000, 512000000000)
    taskconfigs = []
    for j in range(5):
        task_instance_configs = []
        for i in range(10):
            task_instance_configs.append([i, 3000000, 20, None, 70, 10000, 10000, None])
        taskconfigs.append(TaskConfig(j, j * randint(1, 50), task_instance_configs))

    episode = Episode(machine_config, taskconfigs, FirstFitAlgorithm(), None)
    episode.run()
