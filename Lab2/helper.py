from mpi4py import MPI
import argparse
import os
import numpy as np
import math

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


class profiler:
    """
    Profile function calls
    """
    def __init__(self, name:str=None, print_at_exit:bool=True):
        self._name = name
        self._start = None
        self._finish = None
        self._print_at_exit = print_at_exit

    @property
    def name(self):
        return self._name

    @property
    def delta(self):
        return self._finish - self._start

    def __str__(self):
        return "[R#%02d] T:%s. D:%.4fms" % (rank, self.name, self.delta * 1000)

    def __enter__(self):
        self._start = MPI.Wtime()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._finish = MPI.Wtime()
        if self._print_at_exit:
            print(self)


def lab2args(load_data:bool=False):
    parser = argparse.ArgumentParser(description="Lab 2. YAKOBY equations")
    parser.add_argument('coefficient_file', help='File with equation coefficients', type=str)
    parser.add_argument('start_equation_result_file', help='File with equation results file', type=str)
    parser.add_argument('threshold', help='Yakoby method threshold', type=float)
    parser.add_argument('out_file', help='Where to store results', type=str)

    args = parser.parse_args()

    if not os.path.exists(args.coefficient_file):
        raise Exception("Coefficient file not found: %s" % args.coefficient_file)

    if not os.path.exists(args.start_equation_result_file):
        raise Exception("Start equation results file not found: %s" % args.start_equation_result_file)

    if load_data:
        args.coefficients = np.genfromtxt(args.coefficient_file, delimiter=' ')
        args.start_equation_results = np.genfromtxt(args.start_equation_result_file, delimiter=' ')

    args.threshold = math.fabs(args.threshold)

    return args


def lab2out(data:tuple, target_file_path:str):
    np.savetxt(target_file_path, data, fmt='%.10f')


def distribute_tasks_per_processes(num_of_tasks:int, num_of_processes:int) -> tuple:
    """
    Distribute tasks per processes
    :param num_of_tasks: int
    :param num_of_processes: int
    :return: tuple([start, end], [start, end], ..., None)
    """
    need_processes = min(num_of_processes, num_of_tasks)
    tasks_per_process = math.ceil(num_of_tasks / need_processes)
    ret = []

    for i in range(need_processes):
        start_task = tasks_per_process * i
        end_task = tasks_per_process * (i + 1) - 1
        if end_task > num_of_tasks:
            end_task = num_of_tasks
        ret.append((start_task, end_task))

    if need_processes < num_of_processes:
        for q in range(num_of_processes - need_processes):
            ret.append(None)

    return tuple(ret)


class Lab2Tags:
    TEMP_RESULTS = 1