from mpi4py import MPI
from helper import profiler, lab2args, lab2out, distribute_tasks_per_processes, Lab2Tags
import os, sys, math


def calc_equation(variable_index:int, equations:list, last_values:list) -> float:
    b = equations[variable_index][-1]
    all_except_target = sum(a * last_values[i] for i, a in enumerate(equations[variable_index][:-1]) if i != variable_index)
    delim = equations[variable_index][variable_index]
    return 1.0 * (b - all_except_target) / delim


def need_continue_calculation(old_variables:list, new_variables:list, threshold:float) -> bool:
    for a, b in zip(old_variables, new_variables):
        if math.fabs(a - b) > threshold:
            return True
    return False


def work()->None:
    try:
        rank = None
        comm = MPI.COMM_WORLD # type: MPI.Comm
        rank, size = comm.Get_rank(), comm.Get_size()

        if size == 1:
            raise Exception("You should start me with more that one process")

        arguments = lab2args(load_data=True)
        current_variables = arguments.start_equation_results
        count_of_free_processes = size - 1
        equations, variables = arguments.coefficients.shape
        startup_info = distribute_tasks_per_processes(equations, count_of_free_processes)

        if rank == 0:
            print("Common startup info is %s" % (startup_info,))

        common_info = {'finish': 0}  # first - need finish flag
        mine_startup_info = startup_info[rank - 1] if rank != 0 else None
        iter_count = 0

        with profiler("Full proc task at %s" % MPI.Get_processor_name()):
            while common_info['finish'] != 1:
                # Next. Calculate
                if rank != 0:
                    results = []
                    if mine_startup_info is None:
                        pass
                    else:
                        results = [0] * (mine_startup_info[1] - mine_startup_info[0] + 1)
                        for i, idx in enumerate(range(mine_startup_info[0], mine_startup_info[1] + 1)):
                            results[i] = calc_equation(idx, arguments.coefficients, current_variables)
                    comm.send(results, dest=0, tag=Lab2Tags.TEMP_RESULTS)

                if rank == 0:
                    iter_count += 1
                    temp_results_per_process = list(comm.recv(source=proc+1, tag=Lab2Tags.TEMP_RESULTS) for proc in range(count_of_free_processes))
                    new_variables = list(item for sublist in temp_results_per_process for item in sublist)

                    if not need_continue_calculation(current_variables, new_variables, arguments.threshold):
                        common_info['finish'] = 1
                        print("Calculation finished. Iteration count is: %d" % iter_count)

                    current_variables = new_variables

                current_variables = comm.bcast(current_variables, 0)
                common_info = comm.bcast(common_info, 0)

        if rank == 0:
            lab2out(current_variables, arguments.out_file)

    except Exception as exc:
        if not isinstance(rank, int):
            rank = 99
        print("[R#%02d] Exception at %s" % (rank, exc))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

if __name__ == '__main__':
    work()