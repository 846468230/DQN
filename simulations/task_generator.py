from simulations.config import TaskConfig, task_types, accelerators, trace_base, path_base, base
from random import randint
import csv
import os
import numpy as np
from simulations.csvtools import SaveCSV

np.random.seed(5)


def check_it_exits_or_mk(path):
    if not os.path.exists(path):
        os.makedirs(path)


def skip_to(fle, line):
    pos = 0
    for index in range(line + 1):
        pos = fle.tell()
        curline = fle.readline()
    fle.seek(pos)
    return fle


def task_reader(path):
    with open(path, "r", encoding="utf-8") as csvfile:
        spamreader = csv.DictReader(csvfile, )
        single_metrics = list(spamreader)[0]
    with open(path, "r", encoding="utf-8") as csvfile:
        skip_to(csvfile, 2)
        spamreader = csv.DictReader(csvfile)
        datas = list(spamreader)
    return single_metrics, datas


def generate_trace(task_type, task_num, task_sumbit_upper, out_put_dir):
    writer = SaveCSV(keyword_list=['id', 'submit_time', 'task_type'], path=out_put_dir)
    trace = []

    submit_times = np.random.randint(0, task_sumbit_upper, task_num)
    types = np.random.random_integers(0, len(task_type) - 1, task_num)
    submit_times = np.sort(submit_times)
    for i in range(len(submit_times)):
        trace.append({"id": i, "submit_time": submit_times[i], "task_type": task_type[types[i]]})
    for item in trace:
        writer.save(item)


def parse_trace_to_task_instance(item, config_data):
    cpu_data_index = ["throughput", 'cpu_ave_fre', 'cpu1_temp', 'cpu_ave_usage', 'cpu1_power']
    cpu_header_index = ["execute_time"]
    gpu_data_index = ["throughput", 'gpu_pref', 'gpu_temp', 'gpu_power', 'gpu_mem_usage', 'gpu_usage']
    gpu_header_index = ["execute_time"]
    mlu_data_index = ["throughput", 'mlu_phy_mem_usage', 'mlu_vir_mem_usage', 'mlu_temp', 'mlu_power', 'mlu_usage']
    mlu_header_index = ["execute_time"]
    fpga_data_index = ["throughput", 'fpga1_power', 'fpga1_temp']
    fpga_header_index = ["execute_time"]
    task_instance_configs = []
    if item["task_type"] == "resnet50":
        config = config_data["resnet50"]
    else:
        config = {}  # if task more than one type add it here
    instance_config_list = []
    instance_config_list.append(int(item["id"]))
    if "cpu" not in accelerators:  # 改这里。目前cpu用的mlu数据
        cpu_data = config["mlu"]
    else:
        cpu_data = config["cpu"]
    temp = []
    for index in cpu_data_index:
        data = []
        for row in cpu_data["datas"]:
            data.append(round(float(row[index]), 3))
        temp.append(data)
    for index in cpu_header_index:
        temp.append(float(cpu_data["header"][index]))
    if "gpu" not in accelerators:
        gpu_data = None
    else:
        gpu_data = config["gpu"]
    for index in gpu_data_index:
        data = []
        if gpu_data:
            for row in gpu_data["datas"]:
                data.append(round(float(row[index]), 3))
            temp.append(data)
        else:
            temp.append(0.0)  # the shape of this temp is different from obove temp
    for index in gpu_header_index:
        if gpu_data:
            temp.append(float(gpu_data["header"][index]))
        else:
            temp.append(0.0)
    mlu_data = config["mlu"]
    for index in mlu_data_index:
        data = []
        for row in mlu_data["datas"]:
            data.append(round(float(row[index]), 3))
        temp.append(data)
    for index in mlu_header_index:
        temp.append(float(mlu_data["header"][index]))
    fpga_data = config["fpga"]
    for index in fpga_data_index:
        data = []
        for row in fpga_data["datas"]:
            data.append(round(float(row[index]), 3))
        temp.append(data)
    for index in fpga_header_index:
        temp.append(float(fpga_data["header"][index]))
    instance_config_list.extend(temp)
    instance_config_list.append(float(cpu_data["header"]["dataset"]))
    instance_config_list.append(None)
    task_instance_configs.append(instance_config_list)
    return task_instance_configs


def task_generator(trace_path, task_types, accelerators):
    config_data = config_generator(task_types, accelerators)
    task_configs = []
    with open(trace_path, "r", encoding="utf-8") as csvfile:
        spam_reader = csv.DictReader(csvfile)
        spam_reader = list(spam_reader)
    for i in range(len(spam_reader)):
        trace = spam_reader[i]
        task_instance_configs = parse_trace_to_task_instance(item=trace, config_data=config_data)
        task = TaskConfig(i, int(trace["submit_time"]), task_instance_configs)
        task_configs.append(task)
    return task_configs


def test_task_generator():
    taskconfigs = []
    for j in range(5):
        task_instance_configs = []
        for i in range(10):
            task_instance_configs.append([i, 3000000, 20, None, 70, 10000, 10000, None])
        taskconfigs.append(TaskConfig(j, j * randint(1, 50), task_instance_configs))
    return taskconfigs


def config_generator(task_types, accelerators):
    task_all_data = {}
    for task_name in task_types:
        task_card_data = {}
        for item in accelerators:
            task_path = os.path.join(base, "tasks", task_name, item + ".csv")
            header, datas = task_reader(task_path)
            task_card_data[item] = {'header': header, "datas": datas}
        task_all_data[task_name] = task_card_data
    # print(task_card_data["fpga"]["header"]["execute_time"])
    # print(task_card_data["fpga"]["datas"][1]["totol_power"])
    return task_all_data


if __name__ == "__main__":
    task_types = ["resnet50"]
    """ trace generate """
    task_nums = 1000
    task_submit_upper = 10000
    generate_trace_now = False
    if generate_trace_now:  # generate trace files
        check_it_exits_or_mk(trace_base)
        generate_trace(task_types, task_nums, task_submit_upper,
                       os.path.join(trace_base, "_".join(task_types) + ".csv"))

    # task_resnet50 = {}
    # for item in accelerator:
    #     task_path = os.path.join(resnet50,item+".csv")
    #     header,datas = task_reader(task_path)
    #     task_resnet50[item] = {'header':header,"datas":datas}
    # print(task_resnet50["fpga"]["header"]["execute_time"])
    # print(task_resnet50["fpga"]["datas"][1]["totol_power"])
    accelerators = ["fpga", "mlu"]
    # config_generator(task_types, accelerators)
    tasks = task_generator(os.path.join(trace_base, "_".join(task_types) + ".csv"), task_types, accelerators)
    print(tasks)
