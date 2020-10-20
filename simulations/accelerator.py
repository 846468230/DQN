from random import randint
from simulations.csvtools import SaveCSV
from simulations.config import output_logs
import os
from simulations.config import LOG_BASE


class CPUConfig(object):
    idx = 0

    def __init__(self, speed=1, average_frequency=1141, temp=36, power_consumption=65):
        self.speed = speed
        self.average_frequency = average_frequency
        self.temp = temp
        self.power_consumption = power_consumption
        self.id = CPUConfig.idx
        CPUConfig.idx += 1


class GPUConfig(object):
    idx = 0

    def __init__(self, speed=1, level=8, temp=29, power_consumption=24):
        self.speed = speed
        self.level = level
        self.temp = temp
        self.power_consumption = power_consumption
        self.id = GPUConfig.idx
        GPUConfig.idx += 1


class MLUConfig(object):
    idx = 0

    def __init__(self, speed=1, physical_memory_usage=4192, virtual_memory_usage=16643, temp=31, power_consumption=28):
        self.speed = speed
        self.physical_memory_usage = physical_memory_usage
        self.virtual_memory_usage = virtual_memory_usage
        self.power_consumption = power_consumption
        self.temp = temp
        self.id = MLUConfig.idx
        MLUConfig.idx += 1


class FPGAConfig(object):
    idx = 0

    def __init__(self, speed=1, power_consumption=46, temp=43):
        self.speed = speed
        self.power_consumption = power_consumption
        self.temp = temp
        self.id = FPGAConfig.idx
        FPGAConfig.idx += 1


class Accelerator(object):
    def __init__(self, config, env):
        self.id = config.id
        self.speed = config.speed
        self.power_consumption = config.power_consumption
        self.origin_power_consumption = self.power_consumption
        self.temp = config.temp
        self.origin_temp = self.temp
        self.throughput = 0
        self.runtime = None
        self.card_usage = 0
        self.env = env
        self.machine = None
        self.running_task_instance = None
        self.free = env.event()
        self.csv_saver = SaveCSV(self.state, os.path.join(LOG_BASE, self.name + "-" + str(self.id) + ".csv"))

    @property
    def name(self):
        assert NotImplementedError

    @property
    def state(self):
        assert NotImplementedError

    def do_work(self, runtime):
        self.running_task_instance.started = True
        self.running_task_instance.started_timestamp = self.env.now
        self.env.process(self.process_in())
        if not output_logs:
            print(self.state, self.env.now)
        yield self.env.timeout(runtime)
        self.running_task_instance.finished = True
        self.running_task_instance.finished_timestamp = self.env.now
        if output_logs:
            self.csv_saver.save(self.state)
        else:
            print(self.state, self.env.now)
        self.process_out()
        self.free.succeed()
        self.free = self.env.event()

    def attach(self, machine):
        self.machine = machine

    def accommodate(self, task_instance):
        return self.running_task_instance is None

    def caculate_runtime(self):
        if self.runtime is None:
            return randint(0, 180)
        else:
            return self.runtime / self.speed


class FPGA(Accelerator):
    name = "FPGA"

    def __init__(self, fpga_config, env):
        super(FPGA, self).__init__(fpga_config, env)

    def run_task_instance(self, task_instance):
        self.running_task_instance = task_instance
        if hasattr(task_instance, 'fpga_runtime'):
            self.runtime = task_instance.fpga_runtime
        else:
            self.runtime = None
        yield self.env.process(self.do_work(self.caculate_runtime()))

    def process_in(self):
        for i in range(int(self.runtime)):
            self.throughput = self.running_task_instance.fpga_throughput[i]
            self.power_consumption = self.running_task_instance.fpga_power_consumption[i]
            self.temp = self.running_task_instance.fpga_temp[i]
            if output_logs:
                self.csv_saver.save(self.state)
            yield self.env.timeout(1)

    def process_out(self):
        self.throughput = 0
        self.power_consumption = self.origin_power_consumption
        self.temp = self.origin_temp
        self.running_task_instance = None

    @property
    def state(self):
        return {
            'id': FPGA.name + "-" + str(self.id),
            'speed': self.speed,
            'throughput': self.throughput,
            'power_consumption': self.power_consumption,
            'temp': self.temp,
            'running_task_instance': self.running_task_instance,
        }

    def __eq__(self, other):
        return isinstance(other, FPGA) and other.id == self.id


class MLU(Accelerator):
    name = "MLU"

    def __init__(self, mlu_config, env):
        self.physical_memory_usage = mlu_config.physical_memory_usage
        self.origin_physical_memory_usage = self.physical_memory_usage
        self.virtual_memory_usage = mlu_config.virtual_memory_usage
        self.origin_virtual_memory_usage = self.virtual_memory_usage
        super(MLU, self).__init__(mlu_config, env)

    def process_in(self):
        for i in range(int(self.runtime)):
            self.throughput = self.running_task_instance.mlu_throughput[i]
            self.physical_memory_usage = self.running_task_instance.mlu_physical_memory_usage[i]
            self.virtual_memory_usage = self.running_task_instance.mlu_virtual_memory_usage[i]
            self.temp = self.running_task_instance.mlu_temp[i]
            self.power_consumption = self.running_task_instance.mlu_power_consumption[i]
            self.card_usage = self.running_task_instance.mlu_card_usage[i]

            if output_logs:
                self.csv_saver.save(self.state)
            yield self.env.timeout(1)

    def process_out(self):
        self.throughput = 0
        self.physical_memory_usage = self.origin_physical_memory_usage
        self.virtual_memory_usage = self.origin_virtual_memory_usage
        self.temp = self.origin_temp
        self.power_consumption = self.origin_power_consumption
        self.card_usage = 0
        self.running_task_instance = None

    def run_task_instance(self, task_instance):
        self.running_task_instance = task_instance
        if hasattr(task_instance, 'mlu_runtime'):
            self.runtime = task_instance.mlu_runtime
        else:
            self.runtime = None
        yield self.env.process(self.do_work(self.caculate_runtime()))

    @property
    def state(self):
        return {
            'id': MLU.name + "-" + str(self.id),
            'speed': self.speed,
            'throughput': self.throughput,
            'power_consumption': self.power_consumption,
            'card_usage': self.card_usage,
            'physical_memory_usage': self.physical_memory_usage,
            'virtual_memory_usage': self.virtual_memory_usage,
            'temp': self.temp,
            'running_task_instance': self.running_task_instance,
        }

    def __eq__(self, other):
        return isinstance(other, MLU) and other.id == self.id


class GPU(Accelerator):
    name = "GPU"

    def __init__(self, gpu_config, env):
        self.level = gpu_config.level
        self.origin_level = self.level
        self.memory_usage = 0
        super(GPU, self).__init__(gpu_config, env)

    def process_in(self):
        for i in range(int(self.runtime)):
            self.throughput = self.running_task_instance.gpu_throughput[i]
            self.level = self.running_task_instance.gpu_level[i]
            self.temp = self.running_task_instance.gpu_temp[i]
            self.power_consumption = self.running_task_instance.gpu_power_consumption[i]
            self.memory_usage = self.running_task_instance.gpu_memory_usage[i]
            self.card_usage = self.running_task_instance.gpu_usage[i]

            if output_logs:
                self.csv_saver.save(self.state)
            yield self.env.timeout(1)

    def process_out(self):
        self.throughput = 0
        self.level = self.origin_level
        self.temp = self.origin_temp
        self.power_consumption = self.origin_power_consumption
        self.memory_usage = 0
        self.card_usage = 0
        self.running_task_instance = None

    def run_task_instance(self, task_instance):
        self.running_task_instance = task_instance
        if hasattr(task_instance, 'gpu_runtime'):
            self.runtime = task_instance.mlu_runtime
        else:
            self.runtime = None
        yield self.env.process(self.do_work(self.caculate_runtime()))

    @property
    def state(self):
        return {
            'id': GPU.name + "-" + str(self.id),
            'speed': self.speed,
            'throughput': self.throughput,
            'power_consumption': self.power_consumption,
            'card_usage': self.card_usage,
            'level': self.level,
            'memory_usage': self.memory_usage,
            'temp': self.temp,
            'running_task_instance': self.running_task_instance,
        }

    def __eq__(self, other):
        return isinstance(other, GPU) and other.id == self.id


class CPU(Accelerator):
    name = "CPU"

    def __init__(self, cpu_config, env):
        self.average_frequency = cpu_config.average_frequency
        self.origin_average_frequency = self.average_frequency
        super(CPU, self).__init__(cpu_config, env)

    def process_in(self):
        for i in range(int(self.runtime)):
            self.throughput = self.running_task_instance.cpu_throughput[i]
            self.average_frequency = self.running_task_instance.cpu_average_frequency[i]
            self.temp = self.running_task_instance.cpu_temp[i]
            self.card_usage = self.running_task_instance.cpu_usage[i]
            self.power_consumption = self.running_task_instance.cpu_power_consumption[i]

            if output_logs:
                self.csv_saver.save(self.state)
            yield self.env.timeout(1)

    def process_out(self):
        self.throughput = 0
        self.average_frequency = self.origin_average_frequency
        self.temp = self.origin_temp
        self.card_usage = 0
        self.power_consumption = self.origin_power_consumption
        self.running_task_instance = None

    def run_task_instance(self, task_instance):
        self.running_task_instance = task_instance
        if hasattr(task_instance, 'cpu_runtime'):
            self.runtime = task_instance.cpu_runtime
        else:
            self.runtime = None
        yield self.env.process(self.do_work(self.caculate_runtime()))

    @property
    def state(self):
        return {
            'id': CPU.name + "-" + str(self.id),
            'speed': self.speed,
            'throughput': self.throughput,
            'power_consumption': self.power_consumption,
            'card_usage':self.card_usage,
            'average_frequency': self.average_frequency,
            'temp': self.temp,
            'running_task_instance': self.running_task_instance,
        }

    def __eq__(self, other):
        return isinstance(other, CPU) and other.id == self.id


def schedule(env, task, cpu):
    task_instance = task.popleft()
    finished = env.process(cpu.run_task_instance(task_instance))
    yield cpu.free
    if len(task):
        env.process(schedule(env, task, cpu))


if __name__ == "__main__":
    from simpy.rt import RealtimeEnvironment
    from simulations.job import Task
    from simulations.config import TaskConfig
    from collections import deque
    from simulations.config import LOG_BASE

    # print(LOG_BASE)
    cpu_config = CPUConfig(speed=1, frequency=2.3e9, cache=4e6, power_consumption=65, runtime=None)
    env = RealtimeEnvironment(factor=0.01, strict=False)
    cpu = CPU(cpu_config, env)
    task = deque([])
    taskconfigs = []
    for i in range(10):
        taskconfigs.append([i, 3000000, 20, None, 70, 10000, 10000, None])
    taskconfig = TaskConfig(1, 0, taskconfigs)
    onetask = Task(env, taskconfig)
    env.process(schedule(env, deque(onetask.task_instances), cpu))
    env.run()
