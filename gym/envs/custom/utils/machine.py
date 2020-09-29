from enum import Enum


class MachineConfig(object):
    idx = 0

    def __init__(self, cpu_capacity, memory_capacity, disk_capacity, gpu_capacity=None, fpga_capacity=None,
                 mlu_capacity=None, cpu=None, memory=None, disk=None,gpu=None,fpga=None,mlu=None):
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.disk_capacity = disk_capacity

        self.gpu_capacity = gpu_capacity
        self.fpga_capacity = fpga_capacity
        self.mlu_capacity = mlu_capacity

        self.gpu = gpu
        self.fpga= fpga
        self.mlu = mlu

        self.cpu = cpu_capacity if cpu is None else cpu
        self.memory = memory_capacity if memory is None else memory
        self.disk = disk_capacity if disk is None else disk

        self.id = MachineConfig.idx
        MachineConfig.idx += 1


class MachineDoor(Enum):
    TASK_IN = 0
    TASK_OUT = 1
    NULL = 3

class Accelerator(Enum):
    CPU = 0
    GPU = 1
    FPGA = 2
    MLU = 3

class Machine(object):
    def __init__(self, machine_config):
        self.id = machine_config.id
        self.cpu_capacity = machine_config.cpu_capacity
        self.memory_capacity = machine_config.memory_capacity
        self.disk_capacity = machine_config.disk_capacity
        self.cpu = machine_config.cpu
        self.gpu = machine_config.gpu
        self.fpga = machine_config.fpga
        self.mlu = machine_config.mlu
        self.gpu_capacity = machine_config.gpu_capacity
        self.fpga_capacity = machine_config.fpga_capacity
        self.mlu_capacity = machine_config.mlu_capacity
        self.memory = machine_config.memory
        self.disk = machine_config.disk

        self.cluster = None
        self.task_instances = []
        self.machine_door = MachineDoor.NULL

    def _minus_accelerator_capacity(self,task_instance):
        use_types = task_instance.use_types
        for use_type in use_types:
            if use_type is Accelerator.CPU:
                self.cpu_capacity -= task_instance.cpu
            elif use_type is Accelerator.GPU:
                self.gpu_capacity -= task_instance.gpu
            elif use_type is Accelerator.FPGA:
                self.fpga_capacity -= task_instance.fpga
            elif use_type is Accelerator.MLU:
                self.mlu_capacity -= task_instance.mlu

    def _plus_accelerator_capacity(self,task_instance):
        use_types = task_instance.use_types
        for use_type in use_types:
            if use_type is Accelerator.CPU:
                self.cpu_capacity += task_instance.cpu
            elif use_type is Accelerator.GPU:
                self.gpu_capacity += task_instance.gpu
            elif use_type is Accelerator.FPGA:
                self.fpga_capacity += task_instance.fpga
            elif use_type is Accelerator.MLU:
                self.mlu_capacity += task_instance.mlu

    def run_task_instance(self, task_instance):
        self._plus_accelerator_capacity(task_instance)
        self.memory_capacity += task_instance.memory
        self.disk_capacity += task_instance.disk
        self.task_instances.append(task_instance)
        self.machine_door = MachineDoor.TASK_IN

    def stop_task_instance(self, task_instance):
        self._minus_accelerator_capacity(task_instance)
        self.memory_capacity -= task_instance.memory
        self.disk_capacity -= task_instance.disk
        self.machine_door = MachineDoor.TASK_OUT

    @property
    def running_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.started and not task_instance.finished:
                ls.append(task_instance)
        return ls

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
    def feature(self):
        return [self.cpu,self.gpu,self.fpga,self.mlu,self.memory, self.disk]

    @property
    def capacity(self):
        return [self.cpu_capacity,self.gpu_capacity,self.fpga_capacity,self.mlu_capacity,self.memory_capacity, self.disk_capacity]

    @property
    def state(self):
        return {
            'id': self.id,
            'cpu_capacity': self.cpu_capacity,
            'gpu_capacity': self.gpu_capacity,
            'fpga_capacity': self.fpga_capacity,
            'mlu_capacity':self.mlu_capacity,
            'memory_capacity': self.memory_capacity,
            'disk_capacity': self.disk_capacity,
            'cpu': self.cpu,
            'gpu':self.gpu,
            'fpga':self.fpga,
            'mlu':self.mlu,
            'memory': self.memory,
            'disk': self.disk,
            'running_task_instances': len(self.running_task_instances),
            'finished_task_instances': len(self.finished_task_instances)
        }