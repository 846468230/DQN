from .alogrithm import Algorithm


class FirstFitAlgorithm(Algorithm):
    name = "first_fit"

    def __call__(self, machine, clock):
        accelerators = machine.free_accelerators
        tasks = machine.tasks_which_has_waiting_instance
        candidate_task = None
        candidate_accelerator = None

        for accelerator in accelerators:
            for task in tasks:
                if accelerator.accommodate(task):
                    candidate_accelerator = accelerator
                    candidate_task = task
                    break
        return candidate_accelerator, candidate_task
