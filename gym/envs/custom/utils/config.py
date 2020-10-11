
class TaskInstanceConfig(object):
    def __init__(self,instance_index,cpu_cache,cpu_power_consumption,cpu_runtime,cpu_throughput,memory,disk,duration,parent_indices=None):
        self.cpu_cache = cpu_cache
        self.cpu_power_consumption = cpu_power_consumption
        self.cpu_runtime = cpu_runtime
        self.cpu_throughput = cpu_throughput
        self.memory = memory
        self.disk = disk
        self.duration = duration
        self.parent_indices = parent_indices


class TaskConfig(object):
    def __init__(self,idx,submit_time,task_instance_configs):
        self.submit_time = submit_time
        self.task_instance_configs = task_instance_configs
        self.id = idx
