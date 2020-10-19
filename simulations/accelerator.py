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


class CPU(object):
    name = "CPU"

    def __init__(self, cpu_config, env, *args, **kwargs):
        self.id = cpu_config.id
        self.speed = cpu_config.speed
        self.frequency = cpu_config.frequency
        self.cache = cpu_config.cache
        self.origin_cache = cpu_config.cache
        self.power_consumption = cpu_config.power_consumption
        self.origin_power_consumption = cpu_config.power_consumption
        self.throughput = 0
        self.runtime = cpu_config.runtime
        self.env = env
        self.machine = None
        self.running_task_instance = None
        self.free = env.event()
        self.csv_saver = SaveCSV(self.state, os.path.join(LOG_BASE, CPU.name + "-" + str(self.id) + ".csv"))

    def attach(self, machine):
        self.machine = machine

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
        if self.runtime:
            yield self.env.process(self.do_work(self.runtime))
        else:
            yield self.env.process(self.do_work(self.caculate_runtime()))

    def caculate_runtime(self):
        return randint(0, 180)

    def accommodate(self, task_instance):
        return self.cache > task_instance.cpu_cache

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
    cpu = CPU(cpu_config, env, capacity=1)
    task = deque([])
    taskconfigs = []
    for i in range(10):
        taskconfigs.append([i, 3000000, 20, None, 70, 10000, 10000, None])
    taskconfig = TaskConfig(1, 0, taskconfigs)
    onetask = Task(env, taskconfig)
    env.process(schedule(env, deque(onetask.task_instances), cpu))
    env.run()
