from .alogrithm import Algorithm
from .heft_util.core import schedule
from queue import Queue
from functools import partial


class HeftAlgorithm(Algorithm):
    name = "HEFT"

    def __init__(self):
        self.maps = {}
        self.commcost = {}
        self.compcost = {}
        self.valid_pairs = []
        self.mode = "queqe"

    def __call__(self, machine, clock):

        if len(self.valid_pairs) == 0:
            accelerators = machine.accelerators
            tasks = machine.next_needed_scheduled_ten_task_instances()
            if len(tasks)==0:
                return None,None
            self.generate_dag(tasks, clock, accelerators)
            self.schedule()
        if len(self.valid_pairs) and self.valid_pairs[0][0].task.submit_time <= clock:
            candidate_task, candidate_accelerator = self.valid_pairs[0]
            del(self.valid_pairs[0])
        else:
            candidate_task = None
            candidate_accelerator = None
        return candidate_accelerator, candidate_task

    def schedule(self):
        compcost_function = partial(compcost, compcost_dict=self.compcost, agent_map=self.accelerator_maps)
        commcost_function = partial(commcost, commcost_map=self.commcost, task_map=self.maps)
        _, taskson, taskson_order = schedule(self.dag, self.agents, compcost_function, commcost_function)
        for task in taskson_order:
            if task == 0:
                continue  #
            task_instance = self.maps[task]
            accelerator = self.accelerator_maps[taskson[task]]
            task_instance.scheduled = True
            self.valid_pairs.append((task_instance, accelerator))

    def generate_dag(self, tasks, clock, accelerators):
        self.commcost = {task.id: 1 if task.task.submit_time - clock <= 0 else task.task.submit_time - clock
                         for task in tasks}
        self.compcost = {}
        self.maps = {}
        self.accelerator_maps = {}
        for index, accelerator in enumerate(accelerators):
            self.accelerator_maps[index] = accelerator
        self.agents = [i for i in range(len(accelerators))]
        for index, task in enumerate(tasks, 1):
            self.maps[index] = task
            self.compcost[index] = {}
            self.compcost[index]["CPU"] = task.cpu_runtime
            self.compcost[index]["GPU"] = task.gpu_runtime
            self.compcost[index]["MLU"] = task.mlu_runtime
            self.compcost[index]["FPGA"] = task.fpga_runtime
        self.dag = {0: tuple(i for i in range(1, len(tasks) + 1))}
        for i in range(1, len(tasks) + 1):
            self.dag[i] = ()


from simulations.accelerator import CPU, GPU, FPGA, MLU


def compcost(job, agent, compcost_dict, agent_map):
    if job == 0:
        return 0
    cost = compcost_dict[job]
    agent_real = agent_map[agent]
    if isinstance(agent_real, CPU):
        return cost["CPU"]
    elif isinstance(agent_real, GPU):
        return cost["GPU"]
    elif isinstance(agent_real, MLU):
        return cost["MLU"]
    elif isinstance(agent_real, FPGA):
        return cost["FPGA"]


def commcost(ni, nj, A, B, commcost_map, task_map):
    if ni == 0 and nj != 0:
        task = task_map[nj]
        return commcost_map[task.id]
    else:
        return 0
