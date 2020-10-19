import os
from datetime import datetime
import platform

output_logs = False
if platform.system().lower() == 'windows':
    path_base = 'C:\\Users\\dao\\PycharmProjects\\DQN'
else:
    path_base = '/Users/dao/codes/python/DQN'  # # sys.path[0]
os.chmod(path_base, 0o755)
LOG_BASE = os.path.join(path_base, "simulation_logs", datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
if output_logs:
    if not os.path.exists(LOG_BASE):
        os.makedirs(LOG_BASE)
"""task generator configs"""
task_types = ["resnet50"]
accelerators = ["fpga", "mlu"]
base = os.getcwd()
resnet50 = os.path.join(base, "tasks", "resnet50")
trace_base = os.path.join(base, "tasks", "trace")



class TaskInstanceConfig(object):
    def __init__(self, instance_index, cpu_cache, cpu_power_consumption, cpu_throughput, cpu_runtime,
                 gpu_power_consumption, gpu_throughput, gpu_usage, gpu_runtime, mlu_card_power, mlu_throughput,
                 mlu_card_usage, mlu_temp, mlu_runtime,fpga_card_power, fpga_throughput, fpga_temp, fpga_runtime, dataset_num,parent_indices=None):
        self.id = instance_index
        self.cpu_cache = cpu_cache
        self.cpu_power_consumption = cpu_power_consumption
        self.cpu_runtime = cpu_runtime
        self.cpu_throughput = cpu_throughput
        self.gpu_power_consumption = gpu_power_consumption
        self.gpu_throughput = gpu_throughput
        self.gpu_usage = gpu_usage
        self.gpu_runtime = gpu_runtime
        self.mlu_power_consumption = mlu_card_power
        self.mlu_throughput = mlu_throughput
        self.mlu_card_usage = mlu_card_usage
        self.mlu_temp = mlu_temp
        self.mlu_runtime = mlu_runtime
        self.fpga_power_consumption = fpga_card_power
        self.fpga_throughput = fpga_throughput
        self.fpga_temp = fpga_temp
        self.fpga_runtime = fpga_runtime
        self.dataset_num = dataset_num
        self.parent_indices = parent_indices


class TaskConfig(object):
    def __init__(self, idx, submit_time, task_instance_configs):
        self.submit_time = submit_time
        self.task_instance_configs = task_instance_configs
        self.id = idx
