from random import randint
from simulations.csvtools import SaveCSV
from simulations.config import output_logs
import os
from simulations.config import LOG_BASE


class CPUConfig(object):
    idx = 0

    def __init__(self, speed=1, frequency=2.3e9, cache=4e6, power_consumption=65, runtime=None):
        self.speed = speed
        self.frequency = frequency
        self.cache = cache
        self.power_consumption = power_consumption
        self.runtime = runtime
        self.id = CPUConfig.idx
        CPUConfig.idx += 1


class MLUConfig(object):
    idx = 0

    def __init__(self, speed=1, power_consumption=28, temp=31):
        self.speed = speed
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
        self.origin_power_consumption = config.power_consumption
        self.throughput = 0
        self.runtime = None
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
        self.temp = fpga_config.temp
        self.origin_temp = self.temp
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
            self.power_consumption = self.running_task_instance.fpga_power_consumption[i]
            self.throughput = self.running_task_instance.fpga_throughput[i]
            self.temp = self.running_task_instance.fpga_temp[i]
            if output_logs:
                self.csv_saver.save(self.state)
            yield self.env.timeout(1)

    def process_out(self):
        self.power_consumption = self.origin_power_consumption
        self.throughput = 0
        self.running_task_instance = None
        self.temp = self.origin_temp

    @property
    def state(self):
        return {
            'id': FPGA.name + "-" + str(self.id),
            'speed': self.speed,
            'power_consumption': self.power_consumption,
            'temp': self.temp,
            'throughput': self.throughput,
            'running_task_instance': self.running_task_instance,
        }

    def __eq__(self, other):
        return isinstance(other, MLU) and other.id == self.id


class MLU(Accelerator):
    name = "MLU"

    def __init__(self, mlu_config, env):
        self.card_usage = 0
        self.temp = mlu_config.temp
        self.origin_temp = self.temp
        super(MLU, self).__init__(mlu_config, env)

    def process_in(self):
        for i in range(int(self.runtime)):
            self.power_consumption = self.running_task_instance.mlu_power_consumption[i]
            self.throughput = self.running_task_instance.mlu_throughput[i]
            self.card_usage = self.running_task_instance.mlu_card_usage[i]
            self.temp = self.running_task_instance.mlu_temp[i]
            if output_logs:
                self.csv_saver.save(self.state)
            yield self.env.timeout(1)

    def process_out(self):
        self.power_consumption = self.origin_power_consumption
        self.throughput = 0
        self.card_usage = 0
        self.running_task_instance = None
        self.temp = self.origin_temp

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
            'power_consumption': self.power_consumption,
            'temp': self.temp,
            'card_usage': self.card_usage,
            'throughput': self.throughput,
            'running_task_instance': self.running_task_instance,
        }

    def __eq__(self, other):
        return isinstance(other, MLU) and other.id == self.id


class CPU(Accelerator):
    name = "CPU"

    def __init__(self, cpu_config, env):
        self.name = CPU.name
        self.frequency = cpu_config.frequency
        self.cache = cpu_config.cache
        self.origin_cache = cpu_config.cache
        super(CPU, self).__init__(cpu_config, env)

    def process_in(self):
        self.cache -= self.running_task_instance.cpu_cache
        assert self.cache >= 0
        self.power_consumption += self.running_task_instance.cpu_power_consumption
        self.throughput = self.running_task_instance.cpu_throughput

    def process_out(self):
        self.cache += self.running_task_instance.cpu_cache
        assert self.cache == self.origin_cache
        self.power_consumption -= self.running_task_instance.cpu_power_consumption
        assert self.power_consumption == self.origin_power_consumption
        self.throughput = 0
        self.running_task_instance = None

    def do_work(self, runtime):
        self.process_in()
        self.running_task_instance.started = True
        self.running_task_instance.started_timestamp = self.env.now
        if output_logs:
            self.csv_saver.save(self.state)
        else:
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
            'frequency': self.frequency,
            'cache': self.cache,
            'power_consumption': self.power_consumption,
            'throughput': self.throughput,
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
