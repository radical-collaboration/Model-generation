from mpi4py import MPI
import argparse
from impress_md import interface_functions
import pandas as pd
import numpy as np
import itertools

def get_data_tuples(path):
    df = pd.read_csv(args.input_smi, sep=' ', header=None)
    rows = list(map(lambda x : (x[0], x[1]), (df.itertuples(index=False))))
    return rows

def run_docking(smile, name, struct="input/receptor.oeb"):
    # try:
    d_score = interface_functions.RunDocking(smile, struct, name, return_scores=True, write_metrics_out=True)
    interface_functions.ParameterizeOE(name)
    return d_score
    # except KeyboardInterrupt:
    #     print("interupt. Exiting")
    #     exit()
    #     return float('NaN')
    # except:
    #     print("Unknown error. Returning NAN")
    #     return float('NaN')

def get_sublist(l, i):
    return [l[ind] for ind in i]

parser = argparse.ArgumentParser()
parser.add_argument('--input_smi', type=str, required=True)
parser.add_argument('--receptor', type=str, required=True)
parser.add_argument('--output_path', type=str, required=True)
parser.add_argument('--num_rows', type=int, required=False, default=-1)
args = parser.parse_args()


# set up MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
mpisize = comm.Get_size()

# scatter data out to ranks
if rank == 0:
    rows = get_data_tuples(args.input_smi)
    if args.num_rows >= 10:
        rows = rows[:args.num_rows]

    #chunk data for each rank:
    indicies = np.array_split(list(range(len(rows))), mpisize)
    data = [get_sublist(rows, i) for i in indicies]
else:
    data = None

data = comm.scatter(data, root=0)

## do work on data:
scores = []
for work in data:
    scores.append( (work[0], work[1], run_docking(work[0], args.output_path + work[1], struct=args.receptor) ))

## gather data and send back.
data = comm.gather(scores, root=0)
if rank == 0:
    data = list(itertools.chain.from_iterable(data))
    data = pd.DataFrame(data, columns=['smile', 'name', 'dock'])
    data.to_csv(args.output_path + "dock_metrics.csv", index=False, header=True)
else:
    assert data is None