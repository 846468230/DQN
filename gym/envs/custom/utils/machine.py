import os
from enum import Enum
from .Accelerator import CPUConfig, CPU
from gym.envs.custom.utils.csvtools import SaveCSV
from gym.envs.custom.utils.config import LOG_BASE

class MachineConfig(object):
    idx = 0

    def __init__(self, cpu_configs, memory_capacity, disk_capacity, gpu_capacity=None, fpga_capacity=None,
                 mlu_capacity=None, cpu=None, memory=None, disk=None, gpu=None, fpga=None, mlu=None):
        self.cpu_configs = cpu_configs
        self.memory_capacity = memory_capacity
        self.disk_capacity = disk_capacity
        self.memory = memory_capacity if memory is None else memory
        self.disk = disk_capacity if disk is None else disk
        self.id = MachineConfig.idx
        MachineConfig.idx += 1


class MachineDoor(Enum):
    TASK_IN = 0
    TASK_OUT = 1
    NULL = 3


class Machine(object):
    def __init__(self, env, machine_config):
        self.id = machine_config.id
        self.env = env
        self.accelerators = []
        self.cpu_configs = machine_config.cpu_configs
        self.memory_capacity = machine_config.memory_capacity
        self.disk_capacity = machine_config.disk_capacity
        self.cpu_configs = machine_config.cpu_configs
        self.register_accelerator(self.cpu_configs)
        self.memory = machine_config.memory
        self.disk = machine_config.disk
        self.task_instances = []
        self.tasks = []
        self.machine_door = MachineDoor.NULL
        self.csv_saver = SaveCSV(self.state, os.path.join(LOG_BASE, "Machine-" + str(self.id) + ".csv"))

    def register_accelerator(self, configs):
        for config in configs:
            if isinstance(config, CPUConfig):
                self.accelerators.append(
                    CPU(config, self.env))

    def run_task_instance(self, accelerator, task_instance):
        self.memory_capacity -= task_instance.memory
        self.disk_capacity -= task_instance.disk
        accelerator.env.process(accelerator.run_task_instance(task_instance))
        yield accelerator.free
        self.memory_capacity += task_instance.memory
        self.disk_capacity += task_instance.disk

    def accelerators_power_consumption(self, accelerator_class):
        sum_power_consumption = 0
        for accelerator in self.accelerators:
            if isinstance(accelerator, accelerator_class):
                sum_power_consumption += accelerator.power_consumption
        return sum_power_consumption

    def accelerators_throughput(self, accelerator_class):
        sum_throughput = 0
        for accelerator in self.accelerators:
            if isinstance(accelerator, accelerator_class):
                sum_throughput += accelerator.throughput
        return sum_throughput

    @property
    def free_accelerators(self):
        free_accelerators = []
        for accelerator in self.accelerators:
            if accelerator.running_task_instance is None:
                free_accelerators.append(accelerator)
        return free_accelerators

    def add_task(self, task):
        self.tasks.append(task)
        for task_instance in task.task_instances:
            self.task_instances.append(task_instance)

    @property
    def tasks_which_has_waiting_instance(self):
        waiting_task_instances = []
        for task in self.tasks:
            if task.submit_time <= self.env.now:
                for task_instance in task.task_instances:
                    if task_instance.started is False:
                        waiting_task_instances.append(task_instance)
        return waiting_task_instances

    @property
    def running_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.started and not task_instance.finished:
                ls.append(task_instance)
        return ls

    @property
    def has_unfinished_tasks(self):
        for task_instance in self.task_instances:
            if task_instance.finished is False:
                return True
        return False

    @property
    def finished_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.finished:
                ls.append(task_instance)
        return ls

    def attach(self, cluster):
        pass

    def accommodate(self, task):
        pass

    # @property
    # def feature(self):
    #     return [self.cpu, self.gpu, self.fpga, self.mlu, self.memory, self.disk]
    #
    # @property
    # def capacity(self):
    #     return [self.cpu_capacity, self.gpu_capacity, self.fpga_capacity, self.mlu_capacity, self.memory_capacity,
    #             self.disk_capacity]

    @property
    def state(self):
        return {
            'id': self.id,
            'clock':self.env.now,
            'cpus_power_consumption': self.accelerators_power_consumption(CPU),
            'cpus_throughput': self.accelerators_throughput(CPU),
            'memory_capacity': self.memory_capacity,
            'disk_capacity': self.disk_capacity,
            'memory': self.memory,
            'disk': self.disk,
            'running_task_instances': len(self.running_task_instances),
            'finished_task_instances': len(self.finished_task_instances)
        }
