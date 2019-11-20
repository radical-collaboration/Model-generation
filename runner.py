from mpi4py import MPI
import pandas as pd
import sys
import policy
from impress_md import interface_functions

comm = MPI.COMM_WORLD
rank = comm.Get_rank()



def setup_server():
    status_ = MPI.Status()
    storage = {}
    while True:
        
        data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        if len(data) == 1: #pipeline 1
            res = policy.dock_policy(data[0])
            comm.send(int(res), dest=status_.Get_source(), tag=11)
        elif len(data) == 2: #pipeline 2
            res = policy.mmgbsa_minimize_policy(data[0], data[1])
            comm.send(int(res), dest=status_.Get_source(), tag=11)
        elif len(data) == 3: #pipline 3
            res = policy.mmgbsa_ns_policy(data[0], data[1], data[2])
            comm.send(int(res), dest=status_.Get_source(), tag=11)
        else:
            print("got some weird data", data)
            

def worker(df):
    
    struct = "input/"

    start_pos = rank * 100
    for pos in range(start_pos, 10 + start_pos):
        path = "test" + str(pos)  + "/"
        smiles = df.iloc[pos,0]
   
    
        # pipline
        comm.send([smiles], dest=0, tag=11)
        r = comm.recv(source=0, tag=11)
        print("Rank", rank, "should I run docking on", smiles,"?", "\t my model says", bool(r))

        # pipeline
        if r:
            print("Rank", rank, "running docking...")
            score = interface_functions.RunDocking_(smiles,struct,path)
            comm.send([smiles, score], dest=0, tag=11)
            r = comm.recv(source=0, tag=11)
            print("Rank", rank, "should I run minimize, given the docking score", score, "?", "\t my model says", bool(r))
        
            # pipeline
            if r:
                print("Rank", rank, "running param and mini")
                interface_functions.ParameterizeOE(path)
                mscore = interface_functions.RunMinimization_(path, path)
            
            
                comm.send([smiles, score, mscore], dest=0, tag=11)
                r = comm.recv(source=0, tag=11)
                print("Rank", rank, "should I run mmgbsa for 1 ns given a energy minmization result of", mscore, "?\t my model says", bool(r))

        



if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1], sep=' ')
    
    if rank == 0:
        setup_server()
    else:
        worker(df)

        

    
