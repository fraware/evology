import run
import numpy as np
import line_profiler
profile = line_profiler.LineProfiler()
np.random.seed(9)

@profile
def simulation(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates,):
    df, pop = run.run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, False, False)
    return df, pop

simulation(100,0,1000,[1/3, 1/3, 1/3])

''' In command: 
kernprof -v -l evology/code/profile.py > evology/code/profile.txt
kernprof -v -l evology/code/profile.py
kernprof -v -l evology/code/run.py
kernprof -v -l evology/code/run.py > evology/code/profile.txt
 ; no need to be in python env first'''
