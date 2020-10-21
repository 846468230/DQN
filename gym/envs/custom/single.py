import gym


class Single_virtual(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        print('init basic')

    def step(self, action):
        print('step')

    def reset(self):
        print('reset')

    def render(self, mode='human'):
        print('render')

    def close(self):
        print('close')




    # get the throughput of different accelerator
    def get_throughput(self):
        return self.get_cpu_throughput() + self.get_gpu_throughput() + self.get_mlu_throughput() + self.get_fpga_throughput()

    def get_cpu_throughput(self):
        return has_parameter(self, '_cpu_throughput')

    def get_gpu_throughput(self):
        return has_parameter(self, '_gpu_throughput')

    def get_mlu_throughput(self):
        return has_parameter(self, '_mlu_throughput')

    def get_fpga_throughput(self):
        return has_parameter(self, '_fpga_throughput')

    # get the power consumption of different accelerator
    def get_PowerConsumption(self):
        return self.get_cpu_power_consumption() + self.get_gpu_power_consumption() + self.get_mlu_power_consumption() + self.get_fpga_power_consumption()

    def get_cpu_power_consumption(self):
        return has_parameter(self, '_cpu_powerConsumption')

    def get_gpu_power_consumption(self):
        return has_parameter(self, '_gpu_powerConsumption')

    def get_mlu_power_consumption(self):
        return has_parameter(self, '_mlu_powerConsumption')

    def get_fpga_power_consumption(self):
        return has_parameter(self, '_fpga_powerConsumption')
