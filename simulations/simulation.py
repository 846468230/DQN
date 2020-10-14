from simulations.monitor import Monitor


class Simulation(object):
    def __init__(self, env, machine, task_broker, scheduler, event_file):
        self.env = env
        self.machine = machine
        self.task_broker = task_broker
        self.scheduler = scheduler
        self.event_file = event_file
        if event_file is not None:
            self.monitor = Monitor(self)

        self.task_broker.attach(self)
        self.scheduler.attach(self)

    def run(self):
        # Starting monitor process before task_broker process
        # and scheduler process is necessary for log records integrity.
        if self.event_file is not None:
            self.env.process(self.monitor.run())
        self.task_broker.run()
        self.env.process(self.scheduler.run())

    @property
    def finished(self):
        return self.task_broker.destroyed \
               and not self.machine.has_unfinished_tasks
