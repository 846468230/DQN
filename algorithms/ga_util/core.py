import numpy as np
import time
import copy
import math


class GA(object):
    def __init__(self, ITERATION, MODE, DNA_size, DNA_bound, pop_size, plist, CROSS_RATE, MUTATION_RATE, e1, e2, W_time,
                 W_power):
        self.iteration = ITERATION
        self.mode = MODE
        self.DNA_size = DNA_size
        self.DNA_bound = DNA_bound
        self.cross_rate = CROSS_RATE
        self.mutate_rate = MUTATION_RATE
        self.pop_size = pop_size
        self.E1 = e1
        self.E2 = e2
        self.w_time = W_time
        self.w_power = W_power
        self.poplist = plist

    def cost(self, E, p):  # 计算消耗
        c = np.zeros(self.DNA_bound)
        for i in range(self.DNA_size):
            c[p[i]] += E[i, p[i]]
        return np.max(c)

    def get_fitness(self, E, population_list):
        fitness = np.zeros(len(population_list))

        for i in range(len(population_list)):
            fitness[i] = -self.cost(E, population_list[i])
        fitness = fitness - np.min(fitness) + 1
        theta = np.random.rand()
        f = (fitness + abs(np.min(fitness))) / (np.max(fitness) - np.min(fitness) + theta)  # 对适应度值进行标定
        return f

    def Parallel_crossover(self, parent):  # 交叉配对
        child = parent
        if np.random.rand() < self.cross_rate:
            i = np.random.randint(0, self.pop_size)
            cross_points = np.random.randint(0, self.DNA_size)
            parent2 = self.poplist[i]
            child[cross_points:self.DNA_size - 1] = parent2[cross_points:self.DNA_size - 1]  # 将父母的右半部分交换
        return child

    def Weight_crossover(self, parent, E):
        children = []

        for c in range(5):
            child = parent
            if np.random.rand() < self.cross_rate:  # 生成多个child，返回最优child
                i = np.random.randint(0, self.pop_size)
                cross_points = np.random.randint(0, self.DNA_size)
                parent2 = self.poplist[i]
                child[cross_points:self.DNA_size - 1] = parent2[cross_points:self.DNA_size - 1]
                children.append(child)
        fitness = self.get_fitness(E, children)
        return children[np.argmax(fitness)]

    def mutate(self, child):  # 每一位按概率变异
        parent = child;
        for point in range(self.DNA_size):
            if np.random.rand() < self.mutate_rate:
                child[point] = np.random.randint(0, self.DNA_bound)
        return child

    def add_mutate(self, child):  # 种群数量不足时，用于增加个体
        new = child;
        for i in range(5):  # 变异5次
            for point in range(self.DNA_size):
                new[point] = np.random.randint(0, self.DNA_bound)
            return new

    def Similarity(self, p1, p2):  # 定义两个体之间相似度
        s = 0
        for i in range(self.DNA_size):
            s += int(p1[i] == p2[i])      # 这里可能是个bug
        return s / self.DNA_size

    def select(self, E, population_list, best, population_size):  # 按fitness挑选下一代种群
        newlist = []

        fitness = self.get_fitness(self.E1, population_list)
        newlist.append(best)  # 上一代的最好个体直接遗传到下一代
        idx = np.random.choice(range(len(population_list)), size=population_size - 1, replace=True,
                               p=fitness / fitness.sum())
        for i in idx:
            newlist.append(population_list[i])
        population_list = newlist
        fitness = self.get_fitness(E, population_list)
        fsort = np.argsort(fitness)  # 按fitness排序
        k = population_size - 1
        cop = copy.deepcopy(population_list)
        for i in range(round(0.4 * population_size)):  # 对fitness最后40%的个体实施淘汰，用较好个体变异生成的个体补充
            population_list[fsort[i]] = self.add_mutate(cop[fsort[k]])
            k = k - 1

        for i in range(population_size - 1, round(0.5 * population_size), -1):  # 对于fitness前50%的个体，如果太过相似，也会被替换
            if (self.Similarity(newlist[fsort[i]], newlist[fsort[i - 1]])) > 0.7:  # 阈值定为0.7
                population_list[fsort[i - 1]] = self.add_mutate(cop[fsort[i - 1]])

        i = population_size - 1
        while len(population_list) < population_size:  # 种群数量太少会进行补充
            population_list.append(self.add_mutate(cop[fsort[i]]))
            i -= 1
        fitness1 = self.get_fitness(E, population_list)
        best1 = population_list[np.argmax(fitness1)]
        return population_list

    def result(self):  # 返回最终解
        E = self.E1 * self.w_time + self.E2 * self.w_power
        fitness_w = self.get_fitness(E, self.poplist)
        return self.poplist[np.argmax(fitness_w)]

    def Parallel_evolve(self):  # 将群体按评价指标的个数均分为子群体，对每个子群体独立的进行select运算。而后将新生的子群体合并
        k = 1
        last1 = 0
        last2 = 0
        for n in range(self.iteration):
            if k < 100:  # 若最优解连续十次无变化，则加大变异概率
                if k % 10 == 0:
                    self.mutate_rate += 0.05
            pop_copy = copy.deepcopy(self.poplist)
            for parent in pop_copy:
                child = self.Parallel_crossover(parent)
                child = self.mutate(child)
                self.poplist.append(child)
            fitness1 = self.get_fitness(self.E1, self.poplist)
            best1 = self.poplist[np.argmax(fitness1)]  # 保留最优个体
            if best1 == last1:
                k += 1
            last1 = best1
            fitness2 = self.get_fitness(self.E2, self.poplist)
            best2 = self.poplist[np.argmax(fitness2)]
            if best1 == last1:
                k += 1
            last2 = best2
            temp = list(np.random.choice(len(self.poplist), round(len(self.poplist) / 2),
                                         replace=False))  # 随机将种群分为两组，分别实施select动作
            pop1 = [self.poplist[x] for x in temp]
            pop2 = [self.poplist[i] for i in range(len(self.poplist)) if i not in temp]
            a = self.select(self.E1, pop1, best1, round(self.pop_size / 2))
            b = self.select(self.E2, pop2, best2, self.pop_size - round(self.pop_size / 2))
            self.poplist = [i for i in a]  # select完成后合并
            for b1 in b:
                self.poplist.append(b1)

    def Weight_evolve(self):  # 直接用加权评价指标进行select
        k = 1
        last = 0
        E = self.E1 * self.w_time + self.E2 * self.w_power
        for n in range(self.iteration):
            if k < 100:
                if k % 10 == 0:
                    self.mutate_rate += 0.05
            pop_copy = copy.deepcopy(self.poplist)
            for parent in pop_copy:
                child = self.Weight_crossover(parent, E)
                child = self.mutate(child)
                self.poplist.append(child)
            fitness = self.get_fitness(E, self.poplist)
            best = self.poplist[np.argmax(fitness)]
            if best == last:
                k += 1

            last = best
            self.poplist = self.select(E, self.poplist, best, self.pop_size)

    def run(self):
        if (self.mode == "Parallel"):
            self.Parallel_evolve()
        elif (self.mode == "Weight"):
            self.Weight_evolve()