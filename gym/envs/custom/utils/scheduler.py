class Scheduler(object):
    def __init__(self, env, algorithm):
        self.env = env
        self.algorithm = algorithm
        self.simulation = None
        self.machine = None
        self.destroyed = False
        self.valid_pairs = {}

    def attach(self, simulation):
        self.simulation = simulation
        self.machine = simulation.machine

    def make_decision(self):
        while True:
            accelerator, task_instance = self.algorithm(self.machine, self.env.now)
            if accelerator is None or task_instance is None:
                break
            else:
                accelerator.running_task_instance = task_instance
                task_instance.started = True
                self.env.process(
                    accelerator.run_task_instance(
                        task_instance))

    def run(self):
        while not self.simulation.finished:
            self.make_decision()
            yield self.env.timeout(1)
        self.destroyed = True
