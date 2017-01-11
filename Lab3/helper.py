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


def get_cube_size(num_of_processes: int) -> int:
    n = int(math.log2(num_of_processes))
    if num_of_processes != math.pow(2, n):
        return None
    return n


def get_super_cubes(max_cube_size: int, iteration: int) -> tuple:
    result = [0]
    # return list(x for x in range(0, max_cube_size + 1) if range )
    for i in range(max_cube_size, iteration, -1):
        copy = list([x + (1 << (i - 1)) for x in result])
        result += copy
    return result


def get_my_super_cube(iteration: int, current_rank: int) -> int:
    return current_rank & ~((1 << iteration) - 1)


def get_my_childs(iteration: int, current_rank: int) -> tuple:
    result = [current_rank + i for i in range(1, int(math.pow(2, iteration)))]
    return list(result)


def get_my_neighbor_should_send_low(iteration: int, current_rank: int) -> tuple:
    pos = 1 << (iteration - 1)
    if current_rank & pos:
        return current_rank - pos, True
    else:
        return current_rank + pos, False


def get_pivot(data: list, start: int=-1, end: int=-1) -> int:
    if start < 0:
        start = 0
    if end < 0:
        end = len(data) - 1

    index = (start + end + 1) // 2
    return data[index]


def swap(list: list, a: int, b: int) -> None:
    if a == b:
        return
    list[a], list[b] = list[b], list[a]


def quicksort(lst: list) -> None:
    quicksortinner(lst, 0, len(lst) - 1)


def quicksortinner(lst: list, start: int, end: int) -> None:
    if start >= end:
        return
    j = partition(lst, start, end)
    quicksortinner(lst, start, j - 1)
    quicksortinner(lst, j + 1, end)


def partition(array: list, start: int, end: int) -> int:
    pivot = array[end]
    i = start
    for j in range(start, end):
        if array[j] <= pivot:
            swap(array, i, j)
            i += 1
    swap(array, i, end)
    return i


def split_list(pivot: int, data: list, start: int=-1, end: int=-1) -> int:
    if start < 0:
        start = 0
    if end < 0:
        end = len(data) - 1

    pivot = data[(start + end) // 2] if pivot is None else pivot

    i = start
    j = end

    while i < j:
        while data[i] <= pivot and i < j:
            i += 1
        while data[j] >= pivot and i < j:
            j -= 1

        if data[i] > data[j]:
            data[i], data[j] = data[j], data[i]

        if i < j - 1:
            i += 1
        j -= 1

        # now i is first element biggest that pivot

    while data[i] >= pivot and i > start:
        i -= 1

    if data[i] >= pivot:
        i -= 1

    return i + 1


def chunks(l: list, n: int) -> list:
    n = max(1, n)
    return list(l[i:i+n] for i in range(0, len(l), n))


def lab3args(load_data: bool=False) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lab 3. Parallel quick sort")
    parser.add_argument('input_file', help='Input file', type=str)
    parser.add_argument('out_file', help='Where to store results', type=str)

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        raise Exception("Input file not found: %s" % args.input_file)

    if load_data:
        args.data = np.genfromtxt(args.input_file, delimiter=' ', dtype=int)

    return args


def lab3out(data: np.ndarray, target_file_path: str) -> None:
    np.savetxt(target_file_path, data, fmt='%d', newline=' ')


def send_array(array: np.ndarray, comm: MPI.Comm, target: int, tag: int) -> None:
    buffer_size = np.array([len(array), ])
    comm.Send(buffer_size, target, tag=Lab3Tags.BUFFER_SIZE)
    if len(array) > 0:
        comm.Send(array, target, tag=tag)


def recieve_array(comm: MPI.Comm, source: int, tag: int) -> np.ndarray:
    buffer_size_array = np.empty(1, dtype=np.int)
    comm.Recv([buffer_size_array, MPI.INT], source=source, tag=Lab3Tags.BUFFER_SIZE)
    buffer_size = buffer_size_array[0]

    if buffer_size > 0:
        buffer = np.empty(buffer_size, dtype=np.int)
        comm.Recv([buffer, MPI.INT], source=source, tag=tag)  # list
        return buffer
    else:
        return None


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


class Lab3Tags:
    DATA_INIT_CHUNK = 1
    PIVOT = 2
    DATA_LOW_CHUNK = 3
    DATA_HI_CHUNK = 4
    BUFFER_SIZE = 5