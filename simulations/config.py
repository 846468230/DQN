import json
import os
import sys
import csv
from datetime import datetime

output_logs = False
path_base = '/Users/dao/codes/python/DQN'  #'C:\\Users\\dao\\PycharmProjects\\DQN'  # sys.path[0]
os.chmod(path_base,0o755)
LOG_BASE = os.path.join(path_base, "simulation_logs", datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
if output_logs:
    if not os.path.exists(LOG_BASE):
        os.makedirs(LOG_BASE)


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
