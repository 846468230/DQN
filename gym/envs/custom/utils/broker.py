from .job import Task


class Broker(object):
    task_cls = Task

    def __init__(self, env, task_configs):
        self.env = env
        self.simulation = None
        self.machine = None
        self.destroyed = False
        self.task_configs = task_configs

    def attach(self, simulation):
        self.simulation = simulation
        self.machine = simulation.machine

    def run(self):
        for task_config in self.task_configs:
            #assert task_config.submit_time >= self.env.now
            #yield self.env.timeout(task_config.submit_time - self.env.now)
            task = Broker.task_cls(self.env, task_config)
            # print('a task arrived at time %f' % self.env.now)
            self.machine.add_task(task)
        self.destroyed = True
