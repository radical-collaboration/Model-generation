'''
author: Austin Clyde
date: 10/26/2019

sources:
'''

from charm4py import charm
from impress_md import interface_functions

def run_mmgbsa(path):
    interface_functions.RunMinimization(path, path, True)

def main(args):
    #file listing of paths to run this on, pass as argument. One line per path.
    with open('/gpfs/alpine/chm155/world-shared/files.txt', 'r') as f:
        paths_to_run_mmgbsa = map(lambda x : x.strip(), f.readlines())

    result = charm.pool.map(run_mmgbsa, paths_to_run_mmgbsa, chunksize=6)
    exit()

charm.start(main)