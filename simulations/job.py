from .config import *


class Task(object):
    def __init__(self, env, task_config):
        self.env = env
        self.id = task_config.id
        self.task_instance_configs = task_config.task_instance_configs
        self.submit_time = task_config.submit_time
        self._ready = False

        self.task_instances = []
        for task_instance_index in range(len(self.task_instance_configs)):
            task_instance_config = TaskInstanceConfig(*self.task_instance_configs[task_instance_index])
            self.task_instances.append(TaskInstance(env, self, task_instance_index, task_instance_config))
        self.next_instance_pointer = 0

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

    # the most heavy
    def start_task_instance(self, machine):
        self.task_instances[self.next_instance_pointer].schedule(machine)
        self.next_instance_pointer += 1

    @property
    def started(self):
        for task_instance in self.task_instances:
            if task_instance.started:
                return True
        return False

    @property
    def waiting_task_instances_number(self):
        return self.task_config.instances_number - self.next_instance_pointer

    @property
    def has_waiting_task_instances(self):
        return self.task_config.instances_number > self.next_instance_pointer

    @property
    def finished(self):
        """
        A task is finished only if it has no waiting task instances and no running task instances.
        :return: bool
        """
        if self.has_waiting_task_instances:
            return False
        if len(self.running_task_instances) != 0:
            return False
        return True

    @property
    def started_timestamp(self):
        t = None
        for task_instance in self.task_instances:
            if task_instance.started_timestamp is not None:
                if (t is None) or (t > task_instance.started_timestamp):
                    t = task_instance.started_timestamp
        return t

    @property
    def finished_timestamp(self):
        if not self.finished:
            return None
        t = None
        for task_instance in self.task_instances:
            if (t is None) or (t < task_instance.finished_timestamp):
                t = task_instance.finished_timestamp
        return t


class TaskInstance(object):
    def __init__(self, env, task, task_instance_index, task_instance_config):
        self.env = env
        self.task = task
        self.task_instance_index = task_instance_index
        self.config = task_instance_config

        self.cpu_throughput = task_instance_config.cpu_throughput
        self.cpu_average_frequency = task_instance_config.cpu_average_frequency
        self.cpu_temp = task_instance_config.cpu_temp
        self.cpu_usage = task_instance_config.cpu_usage
        self.cpu_power_consumption = task_instance_config.cpu_power_consumption
        self.cpu_runtime = task_instance_config.cpu_runtime

        self.gpu_throughput = task_instance_config.gpu_throughput
        self.gpu_level = task_instance_config.gpu_level
        self.gpu_temp = task_instance_config.gpu_temp
        self.gpu_power_consumption = task_instance_config.gpu_power_consumption
        self.gpu_memory_usage = task_instance_config.gpu_memory_usage
        self.gpu_usage = task_instance_config.gpu_usage
        self.gpu_runtime = task_instance_config.gpu_runtime

        self.mlu_throughput = task_instance_config.mlu_throughput
        self.mlu_physical_memory_usage = task_instance_config.mlu_physical_memory_usage
        self.mlu_virtual_memory_usage = task_instance_config.mlu_virtual_memory_usage
        self.mlu_temp = task_instance_config.mlu_temp
        self.mlu_power_consumption = task_instance_config.mlu_power_consumption
        self.mlu_card_usage = task_instance_config.mlu_card_usage
        self.mlu_runtime = task_instance_config.mlu_runtime

        self.fpga_throughput = task_instance_config.fpga_throughput
        self.fpga_power_consumption = task_instance_config.fpga_power_consumption
        self.fpga_temp = task_instance_config.fpga_temp
        self.fpga_runtime = task_instance_config.fpga_runtime

        # self.memory = task_instance_config.memory
        # self.disk = task_instance_config.disk
        # self.duration = task_instance_config.duration
        self.dataset_num = task_instance_config.dataset_num
        self.parent_indices = task_instance_config.parent_indices

        self.machine = None
        self.accelerator = None
        self.process = None
        self.new = True

        self.started = False
        self.finished = False
        self.started_timestamp = None
        self.finished_timestamp = None

    @property
    def id(self):
        if hasattr(self,'task'):
            return str(self.task.id) + '-' + str(self.task_instance_index)
        else:
            return self.task_instance_index

    def do_work(self):
        # self.cluster.waiting_tasks.remove(self)
        # self.cluster.running_tasks.append(self)
        # self.machine.run(self)
        yield self.env.timeout(self.duration)

        self.finished = True
        self.finished_timestamp = self.env.now

        self.machine.stop_task_instance(self)

    def schedule(self, machine):
        self.started = True
        self.started_timestamp = self.env.now

        self.machine = machine
        self.machine.run_task_instance(self)
        self.process = self.env.process(self.do_work())

    def __repr__(self):
        return f'task_id:{self.id} started:{self.started} started_timestamp:{self.started_timestamp} finished:{self.finished} finished_timestamp:{self.finished_timestamp}'

