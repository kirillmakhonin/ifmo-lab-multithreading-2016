from helper import *
import os, sys


def work() -> None:
    try:
        rank = None
        comm = MPI.COMM_WORLD # type: MPI.Comm
        rank, size = comm.Get_rank(), comm.Get_size()
        n = None

        if size == 1 or rank == 0:
            arguments = lab3args(load_data=rank == 0)

        if size == 1:
            data = quicksort(arguments.data)
            lab3out(data, arguments.out_file)
        else:
            n = get_cube_size(size)
            if n is None:
                raise Exception("Invalid process count: %d" % size)

            if rank == 0:
                data = arguments.data

            with profiler("full task"):
                for iteration in range(n, 0, -1):
                    mine_super_cube = get_my_super_cube(iteration, rank)
                    # print("IT: %d. R: %d. SC: %d" % (iteration, rank, mine_super_cube))

                    if mine_super_cube == rank:
                        if iteration == n:
                            chunk_size = int(len(data) / size)
                            data = chunks(data, chunk_size)
                            mine_data = data[0]
                        else:
                            mine_data = data

                        pivot = get_pivot(mine_data)
                        mine_childs = get_my_childs(iteration, rank)
                        for i, child in enumerate(mine_childs):
                            comm.send(pivot, dest=child, tag=Lab3Tags.PIVOT)
                            if iteration == n:
                                child_data = data[i+1]
                                comm.send(child_data, dest=child, tag=Lab3Tags.DATA_INIT_CHUNK)

                        if iteration == n:
                            data = mine_data

                    else:
                        pivot = comm.recv(source=mine_super_cube, tag=Lab3Tags.PIVOT)
                        if iteration == n:
                            data = np.array(comm.recv(source=mine_super_cube, tag=Lab3Tags.DATA_INIT_CHUNK))

                    pos = split_list(pivot, data) if len(data) > 0 else 0

                    neighbor, send_low = get_my_neighbor_should_send_low(iteration, rank)
                    # print("R%d. N%d. SEND_LOW=%s. P=%d in %s. PIV=%s" % (rank, neighbor, send_low, pos, data, pivot))

                    if send_low: # send low, get hight
                        mine_buffer = data[pos:] # high
                        low = data[:pos]
                        send_array(low, comm, neighbor, Lab3Tags.DATA_LOW_CHUNK)
                    else:
                        recieved = recieve_array(comm, neighbor, Lab3Tags.DATA_LOW_CHUNK)
                        if recieved is None:
                            mine_buffer = data[:pos]
                        else:
                            mine_buffer = np.array(recieved.tolist() + data[:pos].tolist())

                    comm.barrier()

                    if not send_low:  # send low, get hight
                        high = data[pos:]
                        send_array(high, comm, neighbor, Lab3Tags.DATA_HI_CHUNK)
                    else:
                        recieved = recieve_array(comm, neighbor, Lab3Tags.DATA_HI_CHUNK)
                        if recieved is not None:
                            mine_buffer = np.array(mine_buffer.tolist() + recieved.tolist())

                    comm.barrier()

                    mine_buffer.sort() # native sort (in C) - fastest
                    # quicksort(mine_buffer) # Python implementation of sort

                    data = mine_buffer

                    # print("R:%d. Buffer: %s" % (rank, mine_buffer))
                    # sys.stdout.flush()

                    comm.barrier()

                    # if rank == 0:
                    #     print("-" * 30)
                    #     sys.stdout.flush()

                data = comm.gather(data, root=0)
                if rank == 0:
                    data = np.concatenate(data)
                    lab3out(data, arguments.out_file)

    except Exception as exc:
        if not isinstance(rank, int):
            rank = 99

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("[R#%02d] Exception %s at %s:%s. Type:%s" % (rank, exc, fname, exc_tb.tb_lineno, exc_type))

if __name__ == '__main__':
    work()