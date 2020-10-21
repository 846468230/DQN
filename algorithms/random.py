from .alogrithm import Algorithm
import numpy as np


class RandomAlgorithm(Algorithm):
    name = "random"

    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def __call__(self, machine, clock):
        accelerators = machine.free_accelerators
        tasks = machine.tasks_which_has_waiting_instance
        candidate_task = None
        candidate_accelerator = None
        all_candidates = []
        for accelerator in accelerators:
            for task in tasks:
                if accelerator.accommodate(task):
                    all_candidates.append((accelerator, task))
                    if np.random.rand() > self.threshold:
                        candidate_accelerator = accelerator
                        candidate_task = task
                        break
        if len(all_candidates) == 0:
            return None, None
        if candidate_task is None:
            pair_index = np.random.randint(0, len(all_candidates))
            return all_candidates[pair_index]
        else:
            return candidate_accelerator, candidate_task
