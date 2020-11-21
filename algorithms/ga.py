from .alogrithm import Algorithm
import numpy as np
import copy
from algorithms.ga_util.core import GA


class GAAlgorithm(Algorithm):
    name = "GA"

    def __init__(self):
        self.FLAG = 1  # 指示是否完成调度
        self.placement = []  # 调度方案
        self.mode = "queqe"
        self.num = 0
        self.accelerators_init = []
        self.task_init = []
        self.population = 200  # 种群数量
        self.crossover_rate = 0.9  # 配对概率
        self.mutation_rate = 0.05  # 变异概率
        self.iteration = 50  # 迭代次数
        self.w_time = 1  # 时间权重
        self.w_power = 0  # 功耗权重
        self.selectmode = "Parallel"  # 将群体按评价指标的个数均分为子群体，对每个子群体独立的进行select运算。而后将新生的子群体合并
        # self.self.selectmode="Weight"#直接用加权评价指标进行select

    def time_search(self, name, task):  # 获得时间
        if name == "CPU":
            return task.cpu_runtime
        elif name == "GPU":
            return task.gpu_runtime
        elif name == "MLU":
            return task.mlu_runtime
        elif name == "FPGA":
            return task.fpga_runtime
        else:
            pass

    def power_search(self, name, task):  # 获得功耗
        if name == "CPU":
            return task.cpu_power_consumption
        elif name == "GPU":
            return task.gpu_power_consumption
        elif name == "MLU":
            return task.mlu_power_consumption
        elif name == "FPGA":
            return task.fpga_power_consumption
        else:
            pass

    def timeMatrix_init(self, accelerators, tasks):  # 转换为时间矩阵
        E_time = np.zeros((len(tasks), len(accelerators)))
        for i in range(len(tasks)):
            for j in range(len(accelerators)):
                E_time[i, j] = self.time_search(accelerators[j].name, tasks[i])
        return E_time

    def powerMatrix_init(self, accelerators, tasks):  # 转换为功耗矩阵
        E_power = np.zeros((len(tasks), len(accelerators)))
        for i in range(len(tasks)):
            for j in range(len(accelerators)):
                E_power[i, j] = sum(self.power_search(accelerators[j].name, tasks[i]))
        return E_power

    def poplist_init(self, a, t):  # 种群初始化
        population_list = []
        for i in range(self.population):
            nxm_random_num = list(np.random.random_integers(0, a - 1, size=t))
            population_list.append(nxm_random_num)
        return population_list

    def run_GA(self, accelerators, tasks):
        E_time = self.timeMatrix_init(accelerators, tasks)
        E_power = self.powerMatrix_init(accelerators, tasks)
        population_list = self.poplist_init(len(accelerators), len(tasks))
        ga = GA(ITERATION=self.iteration, MODE=self.selectmode, DNA_size=len(tasks), DNA_bound=len(accelerators),
                pop_size=self.population, plist=population_list, CROSS_RATE=self.crossover_rate,
                MUTATION_RATE=self.mutation_rate, e1=E_time, e2=E_power, W_time=self.w_time, W_power=self.w_power)
        ga.run()
        return ga.result()

    def __call__(self, machine, clock):

        tt = []
        for task in machine.tasks:  # 未调度的task
            for task_instance in task.task_instances:
                if task_instance.scheduled is False:
                    tt.append(task_instance)

        accelerators = machine.accelerators
        tasks = tt
        if self.FLAG:
            self.accelerators_init = [accelerator for accelerator in accelerators]
            self.tasks_init = [task for task in tasks]
            self.placement = self.run_GA(accelerators, tasks)
            self.FLAG = 0

        candidate_task = None
        candidate_accelerator = None
        if len(tasks) == 0:
            return candidate_accelerator, candidate_task

        candidate_accelerator = self.accelerators_init[self.placement[self.num]]
        candidate_task = self.tasks_init[self.num]
        self.num += 1
        return candidate_accelerator, candidate_task
