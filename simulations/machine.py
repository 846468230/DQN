import os
from enum import Enum
from .accelerator import CPUConfig, CPU,MLUConfig,FPGAConfig,GPUConfig,MLU,FPGA,GPU
from simulations.csvtools import SaveCSV
from simulations.config import LOG_BASE

class MachineConfig(object):
    idx = 0

    def __init__(self, accelerator_configs, memory_usage , cache_usage,power_base, gpu_capacity=None, fpga_capacity=None,
                 mlu_capacity=None, cpu=None, memory=None, disk=None, gpu=None, fpga=None, mlu=None):
        self.accelerator_configs = accelerator_configs
        self.memory_usage  = memory_usage
        self.cache_usage = cache_usage
        self.power = power_base
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
        self.accelerator_configs = machine_config.accelerator_configs
        self.register_accelerator(self.accelerator_configs)
        self.memory_usage = machine_config.memory_usage
        self.cache_usage = machine_config.cache_usage
        self.power = machine_config.power
        self.task_instances = []
        self.tasks = []
        self.machine_door = MachineDoor.NULL
        self.csv_saver = SaveCSV(self.state, os.path.join(LOG_BASE, "Machine-" + str(self.id) + ".csv"))

    def register_accelerator(self, configs):
        for config in configs:
            if isinstance(config, CPUConfig):
                self.accelerators.append(
                    CPU(config, self.env))
            elif isinstance(config,GPUConfig):
                self.accelerators.append(
                    GPU(config,self.env)
                )
            elif isinstance(config,MLUConfig):
                self.accelerators.append(MLU(config,self.env))
            elif isinstance(config,FPGAConfig):
                self.accelerators.append(FPGA(config,self.env))

    def run_task_instance(self, accelerator, task_instance):
        # self.memory_capacity -= task_instance.memory
        # self.disk_capacity -= task_instance.disk
        accelerator.env.process(accelerator.run_task_instance(task_instance))
        yield accelerator.free
        # self.memory_capacity += task_instance.memory
        # self.disk_capacity += task_instance.disk

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
    def power_total(self):
        sum_power_consumption = 0
        for accelerator in self.accelerators:
            sum_power_consumption += accelerator.power_consumption
        return sum_power_consumption + self.power
    @property
    def throughput_total(self):
        sum_throughput = 0
        for accelerator in self.accelerators:
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

    @property
    def state(self):
        return {
            'id': self.id,
            'clock':self.env.now,
            'cpus_power_consumption': self.accelerators_power_consumption(CPU),
            'cpus_throughput': self.accelerators_throughput(CPU),
            'gpus_power_consumption':self.accelerators_power_consumption(GPU),
            'gpus_throughput':self.accelerators_throughput(GPU),
            'mlus_power_consumption': self.accelerators_power_consumption(MLU),
            'mlus_throughput': self.accelerators_throughput(MLU),
            'fpgas_power_consumption': self.accelerators_power_consumption(FPGA),
            'fpgas_throughput': self.accelerators_throughput(FPGA),
            'power_total': self.power_total,
            'throughput_total':self.throughput_total,
            'memory_usage': self.memory_usage,
            'cache_usage': self.cache_usage,
            'running_task_instances': len(self.running_task_instances),
            'finished_task_instances': len(self.finished_task_instances)
        }
