from simulations.config import output_logs


class Scheduler(object):
    def __init__(self, env, algorithm):
        self.env = env
        if hasattr(algorithm, 'mode'):
            self.mode = "queqe"
        else:
            self.mode = None
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
            if self.mode == "queqe":
                if accelerator and task_instance:
                    self.machine.waiting_instances_queqes[accelerator.name + str(accelerator.id)].put(task_instance)
                    task_instance.scheduled = True
                    break
                else:
                    break
            if accelerator is None or task_instance is None:
                break
            else:
                accelerator.running_task_instance = task_instance
                task_instance.started = True
                self.env.process(self.machine.run_task_instance(accelerator, task_instance))

    def run(self):
        while not self.simulation.finished:
            if self.mode == "queqe":
                for accelerator in self.machine.accelerators:
                    if accelerator.running_task_instance is None and not self.machine.waiting_instances_queqes[
                        accelerator.name + str(accelerator.id)].empty():
                        task_instance = self.machine.waiting_instances_queqes[
                            accelerator.name + str(accelerator.id)].get()
                        accelerator.running_task_instance = task_instance
                        task_instance.started = True
                        self.env.process(self.machine.run_task_instance(accelerator, task_instance))
            self.make_decision()
            if output_logs:
                self.machine.csv_saver.save(self.machine.state)
            # else:
            #     print(self.machine.state)
            yield self.env.timeout(1)
        self.destroyed = True
